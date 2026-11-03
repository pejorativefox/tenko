#!/usr/bin/env bash
# Build the UEFI-only Browneye installer ISO.
#
# Layout on the ISO:
#   /vmlinuz, /initrd.img          kernel and live initramfs
#   /LiveOS/squashfs.img           zstd-compressed live root (dmsquash-live)
#   /boot/efiboot.img              El Torito EFI image with standalone GRUB
#   /grub.cfg                      reference copy of the embedded config
#
# The live root comes from browneye-live (base-runtime + dnf/grub/dracut/
# efibootmgr/dosfstools/LVM2/kernel/python + browneye-installer).  dracut's
# dmsquash-live mounts the squashfs with an overlayfs upper in tmpfs; the
# installer then installs the target packages from the network repository
# (https://tomfool.8bit.ca/browneye/packages/13.1/ by default), so the media
# itself carries no RPMs.
set -euo pipefail
cd "$(dirname "$0")/.."

IMG=${IMG:-localhost/browneye/base:r13.1}
REPO=${REPO:-$PWD/build/repo-all}
KVER=${KVER:-7.3.1}
LIVE=${LIVE:-$PWD/build/live-root}
STAGE=${STAGE:-$PWD/build/iso-stage}
ISO=${ISO:-$PWD/build/browneye-installer.iso}
ISO_LABEL=${ISO_LABEL:-BROWNEYE}
TOOLREPO=${TOOLREPO:-$PWD/build/repo-all}
TOOLS=${TOOLS:-browneye-iso-build}
SKIP_LIVE=${SKIP_LIVE:-0}
ISO_AUTO=${ISO_AUTO:-0}
ISO_ANSWER=${ISO_ANSWER:-}

case "$REPO" in
    http://*|https://*|ftp://*) REPOPATH="$REPO" ;;
    *) REPOPATH="file://$REPO" ;;
esac
if [ "$REPOPATH" != "$REPO" ]; then
    [ -d "$REPO" ] || { echo "missing repo: $REPO" >&2; exit 1; }
fi

if [ "$SKIP_LIVE" != "1" ]; then
    echo "building the live root with browneye-live"
    unshare -r rm -rf "$LIVE"
    mkdir -p "$LIVE/dev"
    # Fake-root builds cannot mknod; regular files are enough for scriptlets.
    for dev in null zero random urandom; do : > "$LIVE/dev/$dev"; done

    unshare -r dnf -y --nogpgcheck \
        --installroot "$LIVE" --releasever=13.1 \
        --disablerepo='*' --repofrompath=browneye,"$REPOPATH" \
        --setopt=install_weak_deps=False \
        install browneye-basefs

    unshare -r dnf -y --nogpgcheck \
        --installroot "$LIVE" --releasever=13.1 \
        --disablerepo='*' --repofrompath=browneye,"$REPOPATH" \
        --setopt=install_weak_deps=False \
        install browneye-live

    for pkg in browneye-live browneye-base-runtime browneye-installer \
               dnf grub dracut efibootmgr efivar dosfstools LVM2 python \
               linux-kernel linux-modules; do
        rpm -q --root "$LIVE" "$pkg" >/dev/null || {
            echo "live root is missing $pkg" >&2; exit 1; }
    done

    if [ -x "$LIVE/usr/bin/systemctl" ]; then
        unshare -r chroot "$LIVE" /usr/bin/systemctl --root=/ preset-all || true
        unshare -r chroot "$LIVE" /usr/bin/systemctl --root=/ set-default multi-user.target || true
    fi

    # The rootfs was assembled without scriptlets, so materialize the baseline
    # accounts (root, nobody, system users) exactly like rootfs_finalize does.
    if [ -x "$LIVE/usr/bin/systemd-sysusers" ]; then
        unshare -r chroot "$LIVE" /usr/bin/systemd-sysusers || true
    fi
    if [ ! -e "$LIVE/etc/shadow" ] && [ -x "$LIVE/usr/sbin/pwconv" ]; then
        unshare -r chroot "$LIVE" /usr/sbin/pwconv || true
        unshare -r chroot "$LIVE" /usr/sbin/grpconv || true
    fi

    # Throwaway console password for debugging the live session only.
    hash=$(openssl passwd -6 live)
    unshare -r sed -i "s|^root:[^:]*:|root:${hash}:|" "$LIVE/etc/shadow"

    "$PWD/scripts/make_initramfs.sh" "$LIVE" "$KVER"
fi

[ -f "$LIVE/boot/vmlinuz-$KVER" ] || { echo "missing kernel" >&2; exit 1; }
[ -f "$LIVE/boot/initramfs-$KVER.img" ] || { echo "missing initramfs" >&2; exit 1; }

# The media carries no packages: installation pulls them from $REPO.
# The authoring tools below still come from the local staged repository.

# One container has the ISO authoring tools (xorriso, mksquashfs); the host
# mounts build/ at /work.  Recreate it every run: the bind mount's :z relabel
# only covers files that existed when it was created, and a freshly built
# live root would otherwise be unreadable to mksquashfs (SELinux silently
# skips it).
podman rm -f "$TOOLS" >/dev/null 2>&1 || true
echo "starting the ISO tools container"
podman run -d --name "$TOOLS" --network=none \
    -v "$PWD/build:/work:z" \
    -v "$TOOLREPO:/repo:ro,z" \
    "$IMG" sleep infinity >/dev/null
podman exec "$TOOLS" /usr/bin/bash -c '
    rpm -Uvh --nodeps --replacepkgs \
        /repo/libburn-*.rpm /repo/libisofs-*.rpm /repo/libisoburn-*.rpm \
        /repo/squashfs-tools-*.rpm /repo/mtools-*.rpm \
        /repo/dosfstools-*.rpm >/dev/null 2>&1
    command -v xorrisofs mksquashfs >/dev/null
'

echo "staging the ISO tree"
rm -rf "$STAGE"
mkdir -p "$STAGE/LiveOS" "$STAGE/boot"
cp -f "$LIVE/boot/vmlinuz-$KVER" "$STAGE/vmlinuz"
cp -f "$LIVE/boot/initramfs-$KVER.img" "$STAGE/initrd.img"

echo "compressing the live root (zstd squashfs)"
podman exec "$TOOLS" mksquashfs /work/live-root /work/iso-stage/LiveOS/squashfs.img \
    -comp zstd -noappend -no-progress \
    -e dev proc sys run tmp

bootargs="root=live:CDLABEL=$ISO_LABEL rd.live.image rd.live.dir=LiveOS rd.live.squashimg=squashfs.img rd.overlay=1 console=tty0 console=ttyS0,115200"
rm -f "$STAGE/answer.json"
if [ -n "$ISO_ANSWER" ]; then
    cp -f "$ISO_ANSWER" "$STAGE/answer.json"
fi
if [ "$ISO_AUTO" = "1" ]; then
    bootargs="$bootargs browneye.auto=1"
fi

cat > "$STAGE/grub.cfg" <<EOF
insmod all_video
insmod iso9660
set timeout=5

menuentry "Browneye Linux 13.1 installer" {
    search --no-floppy --file --set=root /LiveOS/squashfs.img
    linux /vmlinuz $bootargs
    initrd /initrd.img
}
EOF

echo "building the standalone GRUB EFI image"
unshare -r cp "$STAGE/grub.cfg" "$LIVE/tmp/browneye-grub.cfg"
unshare -r chroot "$LIVE" /usr/bin/grub-mkstandalone \
    -O x86_64-efi -o /tmp/BOOTX64.EFI \
    "boot/grub/grub.cfg=/tmp/browneye-grub.cfg"
unshare -r cp "$LIVE/tmp/BOOTX64.EFI" "$STAGE/boot/BOOTX64.EFI"

echo "building the El Torito EFI image"
rm -f "$STAGE/boot/efiboot.img"
mkdir -p "$STAGE/EFI/BOOT"
cp -f "$STAGE/boot/BOOTX64.EFI" "$STAGE/EFI/BOOT/BOOTX64.EFI"
truncate -s 12M "$STAGE/boot/efiboot.img"
# FAT32 needs >=65525 clusters; 12 MiB is below that, so use FAT16 (the
# smallest size mkfs.fat accepts for FAT16; it holds the ~4.7 MiB
# BOOTX64.EFI with plenty of room).  mkfs.fat and mtools live in the ISO
# tools container, not on the host.
podman exec "$TOOLS" mkfs.fat -F 16 -n EFIBOOT /work/iso-stage/boot/efiboot.img >/dev/null
podman exec "$TOOLS" mmd -i /work/iso-stage/boot/efiboot.img ::/EFI ::/EFI/BOOT
podman exec "$TOOLS" mcopy -i /work/iso-stage/boot/efiboot.img \
    /work/iso-stage/boot/BOOTX64.EFI ::/EFI/BOOT/BOOTX64.EFI

echo "writing $ISO"
rm -f "$ISO"
podman exec "$TOOLS" xorrisofs \
    -o "/work/$(basename "$ISO")" \
    -volid "$ISO_LABEL" \
    -J -R \
    -e boot/efiboot.img -no-emul-boot \
    -append_partition 2 0xef /work/iso-stage/boot/efiboot.img \
    -isohybrid-gpt-basdat \
    /work/iso-stage

ls -lh "$ISO"
echo "done"
