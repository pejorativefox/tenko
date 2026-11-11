#!/usr/bin/env bash
# Build the UEFI-only Tenko installer ISO.
#
# Layout on the ISO:
#   /LiveOS/squashfs.img           zstd-compressed live root (dmsquash-live)
#   /boot/efiboot.img              El Torito EFI system partition (FAT32)
#   /answer.json                   optional unattended answer file
#
# The EFI image is a FAT filesystem holding systemd-boot, loader.conf, the
# loader entry and the live kernel/initramfs.  sd-boot only reads FAT (ESP or
# XBOOTLDR), never ISO9660, so everything it loads lives on that image; the
# squashfs stays on the ISO filesystem.
#
# The live root comes from tenko-live (base-runtime + dnf/dracut/
# efibootmgr/dosfstools/LVM2/kernel/python + tenko-installer).  dracut's
# dmsquash-live mounts the squashfs with an overlayfs upper in tmpfs; the
# installer then installs the target packages from the network repository
# (https://tenko.pjfox.xyz/packages/6/ by default), so the media
# itself carries no RPMs.
#
# Usage:
#   tenko image iso
#   ISO_AUTO=1 ISO_ANSWER=tests/installer-answer.json tenko image iso
#
# Environment:
#   REPO        repository for the live root (directory or URL)
#   ISO         output image (default build/tenko-installer.iso)
#   ISO_LABEL   volume label (default TENKO)
#   ISO_AUTO    1 boots the installer unattended with ISO_ANSWER
#   SKIP_LIVE   1 reuses the live root in LIVE (default build/live-root)
#   STAGE, TOOLREPO, TOOLS   staging, tool repo and ISO tool packages
#   BASE_IMAGE, KVER         see scripts/lib/common.sh
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"

REPO=${REPO:-$TENKO_REPO_URL}
LIVE=${LIVE:-$PWD/build/live-root}
STAGE=${STAGE:-$PWD/build/iso-stage}
# Keep the unversioned name until the image is rebuilt; a later build can
# use tenko-installer-6.iso and keep tenko-installer.iso as an alias.
ISO=${ISO:-$PWD/build/tenko-installer.iso}
ISO_LABEL=${ISO_LABEL:-TENKO}
TOOLREPO=${TOOLREPO:-$PWD/build/iso-tools}
TOOLS=${TOOLS:-tenko-iso-build}
SKIP_LIVE=${SKIP_LIVE:-0}
ISO_AUTO=${ISO_AUTO:-0}
ISO_ANSWER=${ISO_ANSWER:-}

REPOPATH=$(repo_url "$REPO")

if [ "$SKIP_LIVE" != "1" ]; then
    echo "building the live root with tenko-live"
    unshare -r rm -rf "$LIVE"
    mkdir -p "$LIVE/dev"
    # Fake-root builds cannot mknod; regular files are enough for scriptlets.
    for dev in null zero random urandom; do : > "$LIVE/dev/$dev"; done

    unshare -r dnf -y --nogpgcheck \
        --installroot "$LIVE" --releasever="$TENKO_RELEASE" \
        --disablerepo='*' --repofrompath=tenko,"$REPOPATH" \
        --setopt=install_weak_deps=False \
        install tenko-basefs

    unshare -r dnf -y --nogpgcheck \
        --installroot "$LIVE" --releasever="$TENKO_RELEASE" \
        --disablerepo='*' --repofrompath=tenko,"$REPOPATH" \
        --setopt=install_weak_deps=False \
        install tenko-live

    for pkg in tenko-live tenko-base-runtime tenko-installer \
               dnf dracut efibootmgr efivar dosfstools btrfs-progs LVM2 \
               python linux-kernel linux-modules; do
        rpm -q --root "$LIVE" "$pkg" >/dev/null || {
            echo "live root is missing $pkg" >&2; exit 1; }
    done

    if [ -x "$LIVE/usr/bin/systemctl" ]; then
        unshare -r chroot "$LIVE" /usr/bin/systemctl --root=/ preset-all || true
        unshare -r chroot "$LIVE" /usr/bin/systemctl --root=/ set-default multi-user.target || true
    fi

    # tenko-base-runtime now includes openssh, and the openssh preset
    # enables sshd.  The live root has a known debugging root password, so
    # never expose sshd on the installation media.
    mkdir -p "$LIVE/etc/systemd/system"
    ln -sfn /dev/null "$LIVE/etc/systemd/system/sshd.service"
    ln -sfn /dev/null "$LIVE/etc/systemd/system/sshd-keygen.service"

    # The rootfs was assembled without scriptlets, so materialize the baseline
    # accounts (root, nobody, system users) exactly like rootfs_finalize does.
    if [ -x "$LIVE/usr/bin/systemd-sysusers" ]; then
        unshare -r chroot "$LIVE" /usr/bin/systemd-sysusers || true
    fi
    if [ ! -e "$LIVE/etc/shadow" ] && [ -x "$LIVE/usr/sbin/pwconv" ]; then
        unshare -r chroot "$LIVE" /usr/sbin/pwconv || true
        unshare -r chroot "$LIVE" /usr/sbin/grpconv || true
    fi

    # The live console must belong to the installer: kmsconvt and
    # firstboot-root-password would otherwise take tty1 and leave a login
    # prompt over the running installer.  45-tenko-live.preset handles the
    # preset state, but remove the enablement links and mask both units so
    # no preset/template ordering can win.
    rm -f "$LIVE/etc/systemd/system/getty.target.wants/kmsconvt@tty1.service"
    rm -f "$LIVE/etc/systemd/system/multi-user.target.wants/tenko-firstboot-root-password.service"
    ln -sfn /dev/null "$LIVE/etc/systemd/system/kmsconvt@tty1.service"
    ln -sfn /dev/null \
        "$LIVE/etc/systemd/system/tenko-firstboot-root-password.service"
    # nmtui runs in a kmscon instance on tty3.  Without this mask, switching
    # there makes systemd-getty-generator start a getty on tty3; logind then
    # activates that session's VT after nmtui exits and the installer never
    # comes back to the foreground.
    ln -sfn /dev/null "$LIVE/etc/systemd/system/getty@tty3.service"
    ln -sfn /dev/null "$LIVE/etc/systemd/system/kmsconvt@tty3.service"

    # A passwordless root shell on tty2 (Ctrl+Alt+F2) and on the serial
    # console makes a broken install recoverable without knowing a password.
    install -d "$LIVE/etc/systemd/system/getty@tty2.service.d"
    cat > "$LIVE/etc/systemd/system/getty@tty2.service.d/autologin.conf" <<'EOF'
[Service]
ExecStart=
ExecStart=-/usr/sbin/agetty --autologin root --noclear %I $TERM
EOF
    ln -sfn /usr/lib/systemd/system/getty@.service \
        "$LIVE/etc/systemd/system/multi-user.target.wants/getty@tty2.service"

    install -d "$LIVE/etc/systemd/system/serial-getty@ttyS0.service.d"
    cat > "$LIVE/etc/systemd/system/serial-getty@ttyS0.service.d/autologin.conf" <<'EOF'
[Service]
ExecStart=
ExecStart=-/usr/sbin/agetty --autologin root --noreset --noclear --keep-baud 115200,57600,38400,9600 - $TERM
EOF

    # The live medium is disposable; root has no password so the rescue
    # shells are immediately usable.  The target system's root stays locked.
    unshare -r sed -i 's|^root:[^:]*:|root::|' "$LIVE/etc/shadow"

    "$PWD/scripts/image/initramfs.sh" "$LIVE" "$KVER"
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
    "$BASE_IMAGE" sleep infinity >/dev/null
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
    bootargs="$bootargs tenko.auto=1"
fi

echo "building the systemd-boot EFI image"
SDBOOT="$LIVE/usr/lib/systemd/boot/efi/systemd-bootx64.efi"
[ -f "$SDBOOT" ] || {
    echo "missing $SDBOOT: systemd was built without -D bootloader=enabled" >&2
    exit 1
}

# Stage the ESP contents outside the ISO tree, so the kernel and initramfs
# are not duplicated on the ISO filesystem.
EFIDIR=$PWD/build/iso-efi
rm -rf "$EFIDIR"
mkdir -p "$EFIDIR/EFI/BOOT" "$EFIDIR/loader/entries"
cp -f "$SDBOOT" "$EFIDIR/EFI/BOOT/BOOTX64.EFI"
cp -f "$LIVE/boot/vmlinuz-$KVER" "$EFIDIR/vmlinuz"
cp -f "$LIVE/boot/initramfs-$KVER.img" "$EFIDIR/initrd.img"

cat > "$EFIDIR/loader/loader.conf" <<EOF
default tenko.conf
timeout 5
console-mode keep
EOF

cat > "$EFIDIR/loader/entries/tenko.conf" <<EOF
title Tenko Linux 6 installer
linux /vmlinuz
initrd /initrd.img
options $bootargs
EOF

# FAT32 requires at least 65525 clusters; 96 MiB holds the ~48 MiB of kernel,
# initramfs and loader with room for a larger initramfs later.  mkfs.fat,
# mtools and xorrisofs live in the ISO tools container, not on the host.
rm -f "$STAGE/boot/efiboot.img"
truncate -s 96M "$STAGE/boot/efiboot.img"
podman exec "$TOOLS" mkfs.fat -F 32 -n TENKOESP /work/iso-stage/boot/efiboot.img >/dev/null
podman exec "$TOOLS" mmd -i /work/iso-stage/boot/efiboot.img \
    ::/EFI ::/EFI/BOOT ::/loader ::/loader/entries
podman exec "$TOOLS" mcopy -i /work/iso-stage/boot/efiboot.img \
    /work/iso-efi/EFI/BOOT/BOOTX64.EFI ::/EFI/BOOT/BOOTX64.EFI
podman exec "$TOOLS" mcopy -i /work/iso-stage/boot/efiboot.img \
    /work/iso-efi/vmlinuz ::/vmlinuz
podman exec "$TOOLS" mcopy -i /work/iso-stage/boot/efiboot.img \
    /work/iso-efi/initrd.img ::/initrd.img
podman exec "$TOOLS" mcopy -i /work/iso-stage/boot/efiboot.img \
    /work/iso-efi/loader/loader.conf ::/loader/loader.conf
podman exec "$TOOLS" mcopy -i /work/iso-stage/boot/efiboot.img \
    /work/iso-efi/loader/entries/tenko.conf ::/loader/entries/tenko.conf

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
