#!/usr/bin/env bash
# Generate /boot/initramfs-$KVER.img inside a staged rootfs.
#
# The kernel RPM does this automatically in its %post scriptlet, but rootfs
# assembly uses `dnf --setopt=tsflags=noscripts`, so the image/ISO build
# scripts must run the same dracut invocation explicitly.
#
# Usage:
#   scripts/make_initramfs.sh [ROOTFS] [KVER]
#
# Environment:
#   OUT   initramfs path inside the rootfs (default /boot/initramfs-$KVER.img)
set -euo pipefail
cd "$(dirname "$0")/.."

ROOTFS=${1:-build/rootfs-desktop}
KVER=${2:-7.2.6}
OUT=${OUT:-/boot/initramfs-$KVER.img}

[ -d "$ROOTFS" ] || { echo "missing rootfs: $ROOTFS" >&2; exit 1; }
[ -d "$ROOTFS/usr/lib/modules/$KVER" ] || {
    echo "missing modules for $KVER in $ROOTFS" >&2; exit 1; }
[ -x "$ROOTFS/usr/bin/dracut" ] || {
    echo "dracut is not installed in $ROOTFS; nothing to generate" >&2; exit 1; }

# A staged rootfs has no devtmpfs yet, and mknod is not permitted in the
# fake-root build.  dracut's helper and shell redirections need /dev/null;
# the real installed system gets proper device nodes from devtmpfs.
mkdir -p "$ROOTFS/dev"
for dev in null zero random urandom; do
    [ -e "$ROOTFS/dev/$dev" ] || : > "$ROOTFS/dev/$dev"
done

echo "generating $OUT for kernel $KVER in $ROOTFS"
# hostonly=no is also set in /etc/dracut.conf.d/10-browneye.conf; pass it
# explicitly so staged rootfs images without the current sysconfig still get
# a generic initramfs.  dracut warns about a missing /proc in the chroot but
# does not need it for a non-hostonly image.
unshare -r chroot "$ROOTFS" /usr/bin/dracut \
    --force --no-hostonly --kver "$KVER" "$OUT"

ls -lh "$ROOTFS$OUT"
