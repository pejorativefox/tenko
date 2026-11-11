#!/usr/bin/env bash
# Boot the desktop in QEMU and run the freedesktop checks inside a real
# LightDM login session.
#
# LightDM autologin gives the checks a logind session and a systemd user
# manager, so they see the same D-Bus activation path as a real user:
# notifications, the portal, the Secret Service, the sound theme, trash, the
# tray, XSettings and the EWMH atoms.  A private dbus-launch bus
# (unix:path=/tmp/dbus-*) is a harness failure, because the portal cannot be
# activated by the user manager on such a bus.
#
# Usage:
#   tenko qemu fdo
#   REPO=http://192.168.31.9/~daspork/tenko/packages/6/ tenko qemu fdo
#   KEEP=1 tenko qemu fdo          # leave QEMU running afterwards
#
# The guest side lives in scripts/qemu/guest/fdo/ and in
# scripts/qemu/fdo_session_check.sh; results are written to
# build/qemu-share/fdo-check.txt.
#
# Exit status:
#   0  every desktop check passed (SKIP is allowed for optional hardware)
#   1  a packaged component failed its check
#   2  the harness could not create a usable session; the reason and the
#      LightDM/Xorg/journal logs are in build/qemu-share/fdo-check.txt
#
# Environment: WAIT (host wait, 420s), SESSION_WAIT (120), TARGET_WAIT (60),
# DESKTOP_WAIT (90), TEST_USER (tenko), TEST_PASSWORD (tenko1), IMGSIZE (6G),
# REBUILD_ROOTFS=1, plus the settings in scripts/lib/qemu.sh (MEM defaults to
# 4096 here).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
MEM=${MEM:-4096}
. scripts/lib/qemu.sh

ROOTFS=${ROOTFS:-$PWD/build/rootfs-fdo}
IMG=${IMG:-$PWD/build/fdo.img}
SERIAL=${SERIAL:-$PWD/build/fdo-serial.log}
MON=${MON:-$PWD/build/fdo-monitor.sock}
SHARE=${SHARE:-$PWD/build/qemu-share}
IMGSIZE=${IMGSIZE:-6G}
WAIT=${WAIT:-420}
SESSION_WAIT=${SESSION_WAIT:-120}
TARGET_WAIT=${TARGET_WAIT:-60}
DESKTOP_WAIT=${DESKTOP_WAIT:-90}
KEEP=${KEEP:-0}
TEST_USER=${TEST_USER:-tenko}
TEST_PASSWORD=${TEST_PASSWORD:-tenko1}
GUEST=scripts/qemu/guest/fdo

start_time=$(date +%s)
test_rootfs "$ROOTFS" desktop
echo "rootfs phase: $(( $(date +%s) - start_time ))s"

# The session targets (xfce-session.target and the autostart entry that
# starts graphical-session.target) come from tenko-desktop-config; without
# them the portal can never be activated and the run would prove nothing.
for path in usr/lib/systemd/user/xfce-session.target \
            usr/lib/systemd/user/xfce-session-watch.service \
            etc/xdg/autostart/xfce-graphical-session.desktop; do
    [ -e "$ROOTFS/$path" ] || {
        echo "harness failure: the image lacks /$path (tenko-desktop-config)" >&2
        exit 2
    }
done
for pkg in lightdm xorg-server xdg-desktop-portal xdg-desktop-portal-gtk \
           gnome-keyring xfce4-session xfce4-notifyd; do
    rpm -q --root "$ROOTFS" "$pkg" >/dev/null 2>&1 || {
        echo "package failure: $pkg is not installed in the desktop set" >&2
        exit 1
    }
done

in=(unshare -r chroot "$ROOTFS")
"${in[@]}" /usr/bin/systemctl --root=/ enable lightdm.service || true
"${in[@]}" /usr/bin/systemctl --root=/ set-default graphical.target || true
"${in[@]}" /usr/bin/systemctl --root=/ mask getty@tty1.service kmsconvt@tty1.service || true

# Guest side: preparation and check scripts, their units, the shared session
# checker, autologin for the test account, and its settings.
libexec=$ROOTFS/usr/local/libexec/fdo-verify
for f in prep.sh check.sh user-check.sh; do
    install -D -m 0755 "$GUEST/$f" "$libexec/$f"
done
install -D -m 0755 scripts/qemu/fdo_session_check.sh \
    "$ROOTFS/usr/local/bin/fdo_session_check.sh"
install -D -m 0644 "$GUEST/fdo-prep.service" "$ROOTFS/etc/systemd/system/fdo-prep.service"
install -D -m 0644 "$GUEST/fdo-check.service" "$ROOTFS/etc/systemd/system/fdo-check.service"
mkdir -p "$ROOTFS/etc/systemd/system/multi-user.target.wants" \
         "$ROOTFS/etc/systemd/system/graphical.target.wants"
ln -sf ../fdo-prep.service "$ROOTFS/etc/systemd/system/multi-user.target.wants/fdo-prep.service"
ln -sf ../fdo-check.service "$ROOTFS/etc/systemd/system/graphical.target.wants/fdo-check.service"

install -D -m 0644 /dev/stdin "$ROOTFS/etc/lightdm/lightdm.conf.d/50-tenko-fdo-verify.conf" <<EOF
[Seat:*]
autologin-user=$TEST_USER
autologin-user-timeout=0
autologin-session=xfce
user-session=xfce
EOF
shquote() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }
{
    printf 'TEST_USER=%s\n' "$(shquote "$TEST_USER")"
    printf 'TEST_PASSWORD=%s\n' "$(shquote "$TEST_PASSWORD")"
} > "$ROOTFS/etc/fdo-verify.env"
printf 'SESSION_WAIT=%s\nTARGET_WAIT=%s\nDESKTOP_WAIT=%s\n' \
    "$SESSION_WAIT" "$TARGET_WAIT" "$DESKTOP_WAIT" > "$ROOTFS/etc/fdo-verify.timeouts"
# tenko-firstboot blocks the display manager until the root password is set;
# this image logs in automatically, so mark that step done.
mkdir -p "$ROOTFS/var/lib/tenko"
echo "skipped by tenko qemu fdo" > "$ROOTFS/var/lib/tenko/firstboot-root-password.done"

disk_image "$ROOTFS" "$IMG" "$IMGSIZE"
mkdir -p "$SHARE"
rm -f "$SHARE/fdo-check.txt" "$SHARE/fdo-check.txt.tmp" "$SHARE/fdo-prep.txt"

qemu_begin=$(date +%s)
qemu_start "$ROOTFS" "$IMG"
[ "$KEEP" = 1 ] && trap - EXIT
result=$SHARE/fdo-check.txt
echo "waiting up to ${WAIT}s for the guest checks (VNC $VNC)"
deadline=$(( $(date +%s) + WAIT ))
while [ "$(date +%s)" -lt "$deadline" ]; do
    if ! qemu_running; then
        echo "harness failure: qemu exited before the guest checks finished" >&2
        break
    fi
    grep -qs '^=== done ===$' "$result" && break
    sleep 2
done

if ! grep -qs '^=== done ===$' "$result"; then
    echo "guest phase: $(( $(date +%s) - qemu_begin ))s (timeout or no result)" >&2
    [ -s "$result.tmp" ] && cat "$result.tmp" >&2
    echo "--- serial tail ---" >&2
    tail -120 "$SERIAL" >&2 || true
    echo "--- prep marker ---" >&2
    cat "$SHARE/fdo-prep.txt" >&2 2>/dev/null || true
    exit 2
fi

echo "guest phase: $(( $(date +%s) - qemu_begin ))s"
cat "$result"
if grep -q '^HARNESS-FAIL' "$result"; then
    echo "freedesktop desktop check: HARNESS FAILURE (the guest session is not usable)" >&2
    exit 2
fi
if grep -q '^FAIL' "$result"; then
    echo "freedesktop desktop check: FAILED" >&2
    exit 1
fi

# A truncated result must not look green: the gate claims these paths.
missing=
for pattern in 'PASS  display' 'PASS  session-bus' 'PASS  user-manager' \
               'PASS  session-targets' 'PASS  desktop-ready' 'PASS  secret-root' \
               'portal: PASS' 'notification-service: PASS' \
               'secret-tool round-trip: tenko-secret' 'gio trash: ok' \
               'pam-keyring: PASS'; do
    grep -qF "$pattern" "$result" || missing="$missing '$pattern'"
done
if [ -n "$missing" ]; then
    echo "harness failure: fdo-check.txt is missing required results:$missing" >&2
    exit 2
fi
echo "total: $(( $(date +%s) - start_time ))s"
echo "freedesktop desktop check: OK"
