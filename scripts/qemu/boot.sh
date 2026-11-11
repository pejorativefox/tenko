#!/usr/bin/env bash
# Boot the installed Tenko rootfs under QEMU.
#
# Prerequisites:
#   - build/rootfs exists and was installed with tenko-base
#   - kernel RPMs for $KVER are in $KERNEL_RPM_DIR (default
#     ~/rpmbuild/RPMS/x86_64)
#
# The script installs linux + linux-modules (and dracut/cpio) into the rootfs,
# creates a raw ext4 image from it, generates the initramfs, boots it with
# virtio-blk/serial, and writes the serial log to build/qemu-boot.log.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
ROOTFS="${ROOTFS:-$PWD/build/rootfs}"
IMG="${IMG:-$PWD/build/rootfs.img}"
LOG="${LOG:-$PWD/build/qemu-boot.log}"
KERNEL_RPM_DIR="${KERNEL_RPM_DIR:-$HOME/rpmbuild/RPMS/x86_64}"
REPO=${REPO:-$TENKO_REPO_URL}
REPOPATH=$(repo_url "$REPO")

[ -x "$ROOTFS/usr/bin/bash" ] || { echo "missing rootfs: $ROOTFS" >&2; exit 1; }
ls "$KERNEL_RPM_DIR"/linux-kernel-"$KVER"-*.rpm "$KERNEL_RPM_DIR"/linux-modules-"$KVER"-*.rpm >/dev/null 2>&1 || {
    echo "missing kernel RPMs for $KVER in $KERNEL_RPM_DIR" >&2
    echo "build them with: OUT=build/kernel tenko build linux/linux.spec" >&2
    echo "then set KERNEL_RPM_DIR=build/kernel/build/linux/RPMS/x86_64" >&2
    exit 1
}

# Make the kernel available to the rootfs transaction.
cp "$KERNEL_RPM_DIR"/linux-kernel-"$KVER"-*.rpm "$KERNEL_RPM_DIR"/linux-modules-"$KVER"-*.rpm "$REPO"/
createrepo_c --quiet --update "$REPO"

unshare -r dnf -y --nogpgcheck \
  --installroot "$ROOTFS" --releasever="$TENKO_RELEASE" \
  --disablerepo='*' --repofrompath=tenko,$REPOPATH \
  --setopt=install_weak_deps=False --setopt=tsflags=noscripts \
  install linux-kernel linux-modules

# systemd-sysusers was disabled in the base build (scripts are skipped at
# install time), so materialize the sysusers baseline before imaging.
if [ -x "$ROOTFS/usr/bin/systemd-sysusers" ]; then
    unshare -r chroot "$ROOTFS" /usr/bin/systemd-sysusers || true
fi

# Apply unit presets offline during the image build.
if [ -x "$ROOTFS/usr/bin/systemctl" ]; then
    unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ preset-all || true
fi

# /etc/machine-id is shipped empty by tenko-sysconfig; systemd generates a
# persistent id on first boot and commits it to the writable root filesystem.

unshare -r chroot "$ROOTFS" /sbin/ldconfig || true

# depmod runs as a package scriptlet, which we skipped above.
depmod -b "$ROOTFS" "$KVER" || true

# The kernel's %post builds the initramfs; scriptlets are skipped here, so do
# the same explicitly.  Boots use it by default (USE_INITRD=1); set
# USE_INITRD=0 to exercise the built-in virtio/ext4 path without one.
USE_INITRD=${USE_INITRD:-1}
initrd=()
if [ -x "$ROOTFS/usr/bin/dracut" ]; then
    "$PWD/scripts/image/initramfs.sh" "$ROOTFS" "$KVER"
    if [ "$USE_INITRD" = 1 ]; then
        initrd=(-initrd "$ROOTFS/boot/initramfs-$KVER.img")
    fi
fi

# Build a raw ext4 image populated directly from the rootfs tree.
rm -f "$IMG"
truncate -s 3G "$IMG"
unshare -r mke2fs -q -t ext4 -d "$ROOTFS" "$IMG"

# Boot with virtio-blk as /dev/vda and serial console.
set +e
timeout 180 qemu-system-x86_64 \
    -enable-kvm -cpu host -m 2048 -smp 4 \
    -kernel "$ROOTFS/boot/vmlinuz-$KVER" \
    "${initrd[@]}" \
    -append "root=/dev/vda rw console=ttyS0 systemd.log_level=info systemd.show_status=1" \
    -drive file="$IMG",format=raw,if=virtio \
    -nographic -no-reboot > "$LOG" 2>&1
rc=$?
set -e
echo "qemu exit: $rc (124 = timeout, expected for a running system)"
tail -80 "$LOG"
