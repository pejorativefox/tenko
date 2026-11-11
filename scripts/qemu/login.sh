#!/usr/bin/env bash
# Boot the desktop through the real first-boot flow and capture the LightDM
# greeter.
#
# The image carries the installer's "desktop" package set with scriptlets
# enabled and a locked root account.  tenko-firstboot prompts on tty1; the
# script types TEST_PASSWORD twice through the QEMU monitor, waits for the
# greeter and captures it (guest xwd over a 9p share, QEMU screendump as the
# fallback).
#
# Usage:
#   tenko qemu login
#   IMAGE_ONLY=1 tenko qemu login        # build the image for tenko qemu run
#   EXTRA_PACKAGES="opencode-bin" tenko qemu login
#
# Output: build/login-firstboot.png, build/login-screenshot.png and the serial
# log build/login-serial.log.  The image is a test artifact: anyone who knows
# TEST_PASSWORD (default tenko1) can log in as root.
#
# Environment: TEST_PASSWORD, TEST_USER (also create a normal account),
# EXTRA_PACKAGES, EXTRA_RPMS (RPM files installed without dependency checks),
# WAIT_BOOT (40), WAIT_GREETER (45), IMGSIZE (6G), REBUILD_ROOTFS=1, plus the
# settings in scripts/lib/qemu.sh.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
. scripts/lib/qemu.sh

ROOTFS=${ROOTFS:-$PWD/build/rootfs-login}
IMG=${IMG:-$PWD/build/login.img}
SERIAL=${SERIAL:-$PWD/build/login-serial.log}
MON=${MON:-$PWD/build/login-monitor.sock}
SHARE=${SHARE:-$PWD/build/qemu-share}
IMGSIZE=${IMGSIZE:-6G}
IMAGE_ONLY=${IMAGE_ONLY:-0}
TEST_PASSWORD=${TEST_PASSWORD:-tenko1}
TEST_USER=${TEST_USER:-}
WAIT_BOOT=${WAIT_BOOT:-40}
WAIT_GREETER=${WAIT_GREETER:-45}
GUEST=scripts/qemu/guest/login

# shellcheck disable=SC2086
test_rootfs "$ROOTFS" desktop ${EXTRA_PACKAGES:-}
if [ -n "${EXTRA_RPMS:-}" ]; then
    # shellcheck disable=SC2086
    unshare -r rpm --root "$ROOTFS" -Uvh --replacepkgs --nodeps $EXTRA_RPMS
fi

in=(unshare -r chroot "$ROOTFS")
# tenko-firstboot asks for the root password on tty1; keep kmscon off that VT
# so the monitor's keystrokes reach the prompt.
"${in[@]}" /usr/bin/systemctl --root=/ mask kmsconvt@tty1.service || true
"${in[@]}" /usr/bin/systemctl --root=/ set-default graphical.target || true
if [ -n "$TEST_USER" ]; then
    # A normal account gives the greeter something to list.
    "${in[@]}" /usr/sbin/useradd -m -c "Test User" "$TEST_USER" 2>/dev/null || true
fi
if "${in[@]}" passwd -S root 2>/dev/null | grep -q '^root P'; then
    die "root already has a password in $ROOTFS; first boot would be skipped"
fi

install -D -m 0755 "$GUEST/greeter-capture.sh" \
    "$ROOTFS/usr/local/libexec/tenko-test/greeter-capture.sh"
install -D -m 0644 "$GUEST/greeter-capture.service" \
    "$ROOTFS/etc/systemd/system/greeter-capture.service"
mkdir -p "$ROOTFS/etc/systemd/system/graphical.target.wants"
ln -sf ../greeter-capture.service \
    "$ROOTFS/etc/systemd/system/graphical.target.wants/greeter-capture.service"

disk_image "$ROOTFS" "$IMG" "$IMGSIZE"
if [ "$IMAGE_ONLY" = 1 ]; then
    echo "image ready: $IMG"
    exit 0
fi

rm -f "$SHARE/greeter.xwd" "$SHARE/greeter-capture.log"
qemu_start "$ROOTFS" "$IMG"

echo "waiting ${WAIT_BOOT}s for the first-boot prompt"
sleep "$WAIT_BOOT"
screendump "$PWD/build/login-firstboot.png" || echo "no first-boot screendump" >&2
echo "typing the first-boot root password on tty1"
sendkeys "$TEST_PASSWORD"
sleep 1
sendkeys "$TEST_PASSWORD"

echo "waiting ${WAIT_GREETER}s for LightDM"
sleep "$WAIT_GREETER"
if [ -s "$SHARE/greeter.xwd" ] && command -v convert >/dev/null 2>&1; then
    convert "$SHARE/greeter.xwd" "$PWD/build/login-screenshot.png"
    echo "screenshot: $PWD/build/login-screenshot.png (guest xwd)"
else
    screendump "$PWD/build/login-screenshot.png" || echo "no greeter screendump" >&2
fi

echo "--- serial tail ---"
tail -40 "$SERIAL" || true
echo "--- capture log ---"
head -30 "$SHARE/greeter-capture.log" 2>/dev/null || true
qemu_stop
