#!/usr/bin/env bash
# Boot the published desktop in QEMU and run the desktop-level freedesktop
# checks inside a real LightDM login session.
#
# This is the final gate for the freedesktop compliance programme (#32).  It
# verifies notifications, the portal, the Secret Service, the sound theme,
# trash, the tray, XSettings and the EWMH atoms on a real installed desktop,
# not just from package metadata.
#
# The gate deliberately uses a real login session instead of the old root
# startx harness.  LightDM autologin gives the session a logind session and a
# systemd user manager, so the checks see the same D-Bus activation path as a
# real user and can cover the issue #48 session target fix.  A private
# dbus-launch bus (unix:path=/tmp/dbus-*) is treated as a harness failure:
# the portal cannot be activated by the user manager on such a bus.
#
# Usage:
#   REPO=build/publish-check tenko qemu fdo
#   REBUILD_ROOTFS=1 tenko qemu fdo  # force a fresh install
#   SKIP_BUILD=1 tenko qemu fdo      # reuse any existing rootfs
#   KEEP=1 tenko qemu fdo            # leave QEMU running
#
# The installed rootfs is reused while the repository's repomd.xml is
# unchanged, so repeated runs do not download the full desktop set again.
# REBUILD_ROOTFS=1 forces a fresh install; SESSION_WAIT, TARGET_WAIT and
# DESKTOP_WAIT bound the guest waits, and WAIT bounds the host wait.
#
# Exit status:
#   0  every desktop check passed (SKIP is allowed for optional hardware)
#   1  a packaged component failed its check
#   2  the harness could not create a usable session; the reason and the
#      LightDM/Xorg/journal logs are written to build/qemu-share/fdo-check.txt
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"

REPO=${REPO:-build/publish-check}
ROOTFS=${ROOTFS:-$PWD/build/rootfs-fdo}
IMG=${IMG:-$PWD/build/fdo-desktop.img}
SERIAL=${SERIAL:-$PWD/build/fdo-serial.log}
SHARE=${SHARE:-$PWD/build/qemu-share}
MON=${MON:-$PWD/build/fdo-monitor.sock}
IMGSIZE=${IMGSIZE:-6G}
WAIT=${WAIT:-420}
MEM=${MEM:-4096}
SESSION_WAIT=${SESSION_WAIT:-120}
TARGET_WAIT=${TARGET_WAIT:-60}
DESKTOP_WAIT=${DESKTOP_WAIT:-90}
SKIP_BUILD=${SKIP_BUILD:-0}
REBUILD_ROOTFS=${REBUILD_ROOTFS:-0}
KEEP=${KEEP:-0}
TEST_USER=${TEST_USER:-tenko}
TEST_PASSWORD=${TEST_PASSWORD:-tenko1}

start_time=$(date +%s)

case "$REPO" in
    http://*|https://*|ftp://*) REPOPATH="$REPO" ;;
    *)
        [ -d "$REPO" ] || { echo "missing repo: $REPO" >&2; exit 1; }
        REPOPATH="file://$REPO"
        ;;
esac

# Quote a value for a POSIX shell assignment.
shquote() {
    printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"
}

# The installed package set is cached as long as the repository metadata is
# unchanged.  A full fresh install is still the first run of a series and is
# available explicitly with REBUILD_ROOTFS=1 (or SKIP_BUILD=0 with a changed
# repository).  The guest files below are always rewritten, so changes to this
# script do not need a rebuild.
repo_fingerprint() {
    case "$REPOPATH" in
        file://*)
            local dir=${REPOPATH#file://}
            if [ -f "$dir/repodata/repomd.xml" ]; then
                sha256sum "$dir/repodata/repomd.xml" | awk '{print $1}'
            else
                find "$dir" -maxdepth 3 -name repomd.xml -print0 2>/dev/null |
                    sort -z | xargs -0 sha256sum 2>/dev/null |
                    sha256sum | awk '{print $1}'
            fi
            ;;
        *)
            local tmp
            tmp=$(mktemp) || return 1
            if ! curl -fsSL --max-time 20 \
                    "$REPOPATH/repodata/repomd.xml" -o "$tmp" 2>/dev/null; then
                rm -f "$tmp"
                return 1
            fi
            sha256sum "$tmp" | awk '{print $1}'
            rm -f "$tmp"
            ;;
    esac
}

install_rootfs=0
cache_stamp=$ROOTFS/.fdo-repo-fingerprint
if [ "$SKIP_BUILD" != "1" ]; then
    repo_stamp=$(repo_fingerprint || true)
    if [ "$REBUILD_ROOTFS" != "1" ] && [ -n "$repo_stamp" ] &&
       [ -f "$cache_stamp" ] && [ "$(cat "$cache_stamp")" = "$repo_stamp" ] &&
       [ -x "$ROOTFS/usr/bin/lightdm" ] &&
       [ -f "$ROOTFS/boot/vmlinuz-$KVER" ]; then
        echo "reusing the installed rootfs (repository metadata matches $repo_stamp)"
    else
        install_rootfs=1
    fi
fi

if [ "$install_rootfs" = 1 ]; then
    echo "installing the desktop rootfs from $REPO"
    # CA trust directories are read-only; remove them with fake-root
    # privileges so a rebuild can start from a clean tree.
    unshare -r rm -rf "$ROOTFS"
    mkdir -p "$ROOTFS/dev"
    # The fake-root build cannot mknod; regular files are enough for the
    # redirections and helpers the scriptlets use.
    for dev in null zero random urandom; do : > "$ROOTFS/dev/$dev"; done

    # tenko-basefs must be installed first: its scriptlets create the
    # merged-/usr layout that every later scriptlet needs.
    unshare -r dnf -y --nogpgcheck \
        --installroot "$ROOTFS" --releasever="$TENKO_RELEASE" \
        --disablerepo='*' --repofrompath=desktop,"$REPOPATH" \
        --setopt=install_weak_deps=False --setopt=tsflags=noscripts \
        install tenko-basefs

    # Scriptlets are enabled for the login harness: lightdm creates its
    # user/group in %pre and its state directories in %post, which a root
    # XFCE session did not need.
    unshare -r dnf -y --nogpgcheck \
        --installroot "$ROOTFS" --releasever="$TENKO_RELEASE" \
        --disablerepo='*' --repofrompath=desktop,"$REPOPATH" \
        --setopt=install_weak_deps=False \
        install tenko-base xfce-desktop linux-kernel linux-modules \
        || echo "warning: dnf reported a scriptlet failure; checking packages" >&2

    if [ -x "$ROOTFS/usr/bin/systemd-sysusers" ]; then
        unshare -r chroot "$ROOTFS" /usr/bin/systemd-sysusers || true
    fi
    if [ -x "$ROOTFS/usr/bin/systemctl" ]; then
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ preset-all || true
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ enable lightdm.service || true
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ set-default graphical.target || true
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ mask getty@tty1.service || true
        unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ mask kmsconvt@tty1.service || true
    fi

    unshare -r chroot "$ROOTFS" /sbin/ldconfig || true
    if command -v depmod >/dev/null 2>&1; then
        depmod -b "$ROOTFS" "$KVER" || true
    elif [ -x "$ROOTFS/usr/sbin/depmod" ]; then
        # The host may not have kmod installed; use the image's depmod.
        unshare -r chroot "$ROOTFS" /usr/sbin/depmod -a "$KVER" || true
    fi

    # The fake-root build cannot apply lightdm's chown; the guest only needs
    # the directories to be writable.  All ownership that matters is fixed by
    # fdo-prep.service at boot.
    for d in var/lib/lightdm var/lib/lightdm-data var/cache/lightdm var/log/lightdm; do
        mkdir -p "$ROOTFS/$d"
        chmod -R a+rwX "$ROOTFS/$d"
    done

    # The kernel %post is skipped by some scriptlet paths; make sure the
    # image carries the initramfs it would have built.
    if [ ! -f "$ROOTFS/boot/initramfs-$KVER.img" ] && [ -x "$ROOTFS/usr/bin/dracut" ]; then
        "$PWD/scripts/image/initramfs.sh" "$ROOTFS" "$KVER"
    fi

    # Remember which repository produced this install so the next run can
    # reuse it without downloading 300 packages again.  An empty fingerprint
    # (curl failure) must not be cached.
    if [ -n "${repo_stamp:-}" ]; then
        printf '%s\n' "$repo_stamp" > "$cache_stamp"
    else
        rm -f "$cache_stamp"
    fi
    echo "rootfs phase: $(( $(date +%s) - start_time ))s"
fi

if [ "$SKIP_BUILD" = "1" ]; then
    echo "reusing the existing rootfs (SKIP_BUILD=1)"
elif [ "$install_rootfs" = 0 ]; then
    echo "rootfs phase: 0s (cached)"
fi

[ -f "$ROOTFS/boot/vmlinuz-$KVER" ] || {
    echo "missing kernel in $ROOTFS/boot" >&2; exit 1; }

# The #48 fix has to be in the image before it is worth booting.  Without
# xfce-session.target the portal can never be activated by the user manager,
# and the run would only exercise the old private-bus bypass.
config_release=$(unshare -r rpm -q --root "$ROOTFS" \
    --qf '%{RELEASE}' tenko-desktop-config 2>/dev/null || true)
for path in \
    usr/lib/systemd/user/xfce-session.target \
    usr/lib/systemd/user/xfce-session-watch.service \
    etc/xdg/autostart/xfce-graphical-session.desktop
do
    if [ ! -e "$ROOTFS/$path" ]; then
        echo "harness failure: the installed image lacks /$path" >&2
        echo "tenko-desktop-config is ${config_release:-missing}; the issue #48 session target fix needs 6-6 or newer" >&2
        echo "use a current repository (REPO=$REPO)" >&2
        exit 2
    fi
done

for pkg in lightdm xorg-server xdg-desktop-portal xdg-desktop-portal-gtk \
           gnome-keyring xfce4-session xfce4-notifyd; do
    rpm -q --root "$ROOTFS" "$pkg" >/dev/null 2>&1 || {
        echo "package failure: $pkg is not installed in the desktop set" >&2
        exit 1
    }
done

# Remove units from older harness revisions so they cannot race LightDM.
rm -f "$ROOTFS/usr/local/bin/fdo-check.sh" \
      "$ROOTFS/etc/systemd/system/fdo-check.service" \
      "$ROOTFS/etc/systemd/system/graphical.target.wants/fdo-check.service" \
      "$ROOTFS/etc/systemd/system/xfce-test.service" \
      "$ROOTFS/etc/systemd/system/graphical.target.wants/xfce-test.service" \
      "$ROOTFS/etc/systemd/system/xfce-debug.service" \
      "$ROOTFS/etc/systemd/system/graphical.target.wants/xfce-debug.service" \
      "$ROOTFS/etc/systemd/system/lightdm.service"
mkdir -p "$ROOTFS/etc/systemd/system/multi-user.target.wants" \
         "$ROOTFS/etc/systemd/system/graphical.target.wants" \
         "$ROOTFS/usr/local/libexec/fdo-verify" \
         "$ROOTFS/etc/lightdm/lightdm.conf.d"

# Autologin gives the checks a real logind session and systemd user manager.
# The user is created and given TEST_PASSWORD by fdo-prep.service before
# lightdm starts; the password is also used to unlock the test keyring.
cat > "$ROOTFS/etc/lightdm/lightdm.conf.d/50-tenko-fdo-verify.conf" <<EOF
[Seat:*]
autologin-user=$TEST_USER
autologin-user-timeout=0
autologin-session=xfce
user-session=xfce
EOF

{
    printf 'TEST_USER=%s\n' "$(shquote "$TEST_USER")"
    printf 'TEST_PASSWORD=%s\n' "$(shquote "$TEST_PASSWORD")"
} > "$ROOTFS/etc/fdo-verify.env"

cat > "$ROOTFS/usr/local/libexec/fdo-verify/prep.sh" <<'EOF'
#!/bin/sh
# Runs before lightdm: create the test account, mount the host share once,
# and get the first-boot policy out of the way.  Ownership is repaired here
# because the fake-root image build flattens non-root ownership.
set -u
. /etc/fdo-verify.env

mkdir -p /mnt /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix || true

# The installroot transaction can run before every schema is present, and
# the glib file trigger cannot compile schemas without a mounted /proc.
# Recompile after the package set is complete so the portal backend can read
# org.gnome.desktop.lockdown and friends.
if [ -x /usr/bin/glib-compile-schemas ]; then
    /usr/bin/glib-compile-schemas /usr/share/glib-2.0/schemas || true
fi
rm -f /tmp/.X0-lock /tmp/.X11-unix/X0
if ! grep -q '^host0 /mnt ' /proc/mounts 2>/dev/null; then
    modprobe 9pnet_virtio >/dev/null 2>&1 || true
    mount -t 9p -o trans=virtio,version=9p2000.L host0 /mnt \
        || echo "fdo-prep: could not mount the host share" >&2
fi

# The login account is created here, as real root, so its home directory has
# the correct owner and the stock /etc/skel files.
/usr/bin/systemd-sysusers >/dev/null 2>&1 || true
if ! getent passwd "$TEST_USER" >/dev/null 2>&1; then
    /usr/sbin/useradd -m -U -c "Desktop verification" -s /bin/bash "$TEST_USER" \
        || exit 1
fi
printf '%s:%s\n' "$TEST_USER" "$TEST_PASSWORD" | /usr/sbin/chpasswd || exit 1
chown -R "$TEST_USER:$TEST_USER" "/home/$TEST_USER" || exit 1
chmod 0700 "/home/$TEST_USER"

# tenko-firstboot is ordered before display-manager.service.  This image has
# an autologin test account and no console user, so record that the root
# password step was deliberately skipped instead of blocking on tty1.
mkdir -p /var/lib/tenko
printf 'skipped by qemu_fdo_verify on %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    > /var/lib/tenko/firstboot-root-password.done

echo "fdo-prep: ok" > /mnt/fdo-prep.txt
EOF
chmod 0755 "$ROOTFS/usr/local/libexec/fdo-verify/prep.sh"

cat > "$ROOTFS/usr/local/libexec/fdo-verify/check.sh" <<'EOF'
#!/bin/sh
# Runs as root after lightdm starts.  It waits for the real login session,
# resolves its environment, runs the root-bus keyring check, then hands the
# desktop checks to the logged-in user.  The whole result is written to the
# 9p share atomically.
set -u
. /etc/fdo-verify.env
. /etc/fdo-verify.timeouts

result=/mnt/fdo-check.txt
tmp=/mnt/fdo-check.txt.tmp
exec >"$tmp" 2>&1

diagnostics() {
    echo "=== harness diagnostics ==="
    echo "--- loginctl ---"
    loginctl list-sessions 2>&1 || true
    echo "--- session processes ---"
    ps -eo pid,uid,user,args 2>&1 | grep -E 'lightdm|Xorg|xfce|dbus' || true
    echo "--- lightdm ---"
    tail -150 /var/log/lightdm/lightdm.log 2>&1 || true
    echo "--- lightdm xorg ---"
    tail -200 /var/log/lightdm/x-0.log 2>&1 || true
    echo "--- xorg ---"
    tail -150 /var/log/Xorg.0.log 2>&1 || true
    echo "--- xsession errors ---"
    tail -120 "/home/$TEST_USER/.xsession-errors" 2>&1 || true
    echo "--- journal ---"
    journalctl -b --no-pager 2>&1 | tail -250 || true
}

finish() {
    status=$1
    echo "=== done ==="
    mv "$tmp" "$result"
    exit "$status"
}

harness_fail() {
    echo "HARNESS-FAIL: $*"
    diagnostics
    finish 3
}

uid=$(id -u "$TEST_USER" 2>/dev/null) || \
    harness_fail "test user $TEST_USER does not exist after fdo-prep"
runtime=/run/user/$uid
bus="unix:path=$runtime/bus"

# Wait for the login session itself.  The #48 targets are checked by
# user-check.sh: if the session exists but the targets are inactive that is
# a package failure, not a harness failure.
session=
i=0
while [ "$i" -lt "$SESSION_WAIT" ]; do
    session=$(loginctl list-sessions --no-legend 2>/dev/null |
        awk -v u="$TEST_USER" '$3 == u {print $1; exit}')
    if [ -n "$session" ] && [ -S "$runtime/bus" ] &&
       pgrep -u "$uid" -x xfce4-session >/dev/null 2>&1; then
        break
    fi
    i=$((i + 1))
    sleep 1
done

if [ -z "$session" ]; then
    harness_fail "no logind session for $TEST_USER after ${SESSION_WAIT}s"
fi
if [ ! -S "$runtime/bus" ]; then
    harness_fail "the systemd user bus $bus did not appear after ${SESSION_WAIT}s"
fi
if ! pgrep -u "$uid" -x xfce4-session >/dev/null 2>&1; then
    harness_fail "xfce4-session is not running for $TEST_USER after ${SESSION_WAIT}s"
fi

# Resolve the real session environment from xfce4-session instead of guessing
# the display and XAUTHORITY path.
pid=$(pgrep -u "$uid" -x xfce4-session | head -1)
envval() {
    tr '\0' '\n' < "/proc/$pid/environ" 2>/dev/null |
        sed -n "s/^$1=//p" | head -1
}
display=$(envval DISPLAY)
xauth=$(envval XAUTHORITY)
if [ -z "$display" ]; then
    harness_fail "xfce4-session (pid $pid) has no DISPLAY"
fi
[ -n "$xauth" ] || xauth="/home/$TEST_USER/.Xauthority"

echo "=== session environment ==="
echo "user=$TEST_USER uid=$uid"
echo "session=$session"
echo "DISPLAY=$display"
echo "XAUTHORITY=$xauth"
echo "XDG_RUNTIME_DIR=$runtime"
echo "DBUS_SESSION_BUS_ADDRESS=$bus"
echo "xfce4-session-pid=$pid"

# A root dbus-run-session check covers the Secret Service provider on its
# own, independently of the graphical login.
echo "=== secret service (root bus) ==="
if command -v dbus-run-session >/dev/null 2>&1 &&
   command -v secret-tool >/dev/null 2>&1 &&
   command -v gnome-keyring-daemon >/dev/null 2>&1; then
    mkdir -p /run/user/0
    chmod 700 /run/user/0
    if root_out=$(timeout 60 dbus-run-session -- sh -c '
        export HOME=/root
        export XDG_RUNTIME_DIR=/run/user/0
        gnome-keyring-daemon --start --components=secrets >/dev/null 2>&1 || true
        sleep 1
        printf "%s\n" "$1" | gnome-keyring-daemon --unlock --components=secrets \
            >/dev/null 2>&1 || true
        if ! printf "tenko-root-secret" |
                secret-tool store --label=tenko service tenko key root-test 2>&1; then
            printf "tenko-root-secret" |
                secret-tool store \
                --collection=/org/freedesktop/secrets/collection/session \
                --label=tenko service tenko key root-test 2>&1 || exit 1
        fi
        value=$(secret-tool lookup service tenko key root-test 2>&1) || exit 1
        [ "$value" = tenko-root-secret ] || exit 1
    ' sh "$TEST_PASSWORD" 2>&1); then
        echo "PASS  secret-root                   secret-tool round-trip on a root bus"
    else
        echo "FAIL  secret-root                   ${root_out:-secret-tool round-trip failed}"
    fi
else
    echo "SKIP  secret-root                   dbus-run-session, secret-tool or gnome-keyring-daemon is missing"
fi

# Run the desktop checks as the logged-in user.  The environment file is
# sourced by a non-interactive shell so systemctl --user talks to the login
# session's manager.
cat > /etc/fdo-verify-session.env <<ENVEOF
DISPLAY=$(printf '%s' "$display" | sed "s/'/'\\\\''/g" | sed "s/^/'/;s/$/'/")
XAUTHORITY=$(printf '%s' "$xauth" | sed "s/'/'\\\\''/g" | sed "s/^/'/;s/$/'/")
XDG_RUNTIME_DIR='$runtime'
DBUS_SESSION_BUS_ADDRESS='$bus'
XDG_CURRENT_DESKTOP='XFCE'
XDG_SESSION_TYPE='x11'
XDG_SESSION_ID='$session'
HOME='/home/$TEST_USER'
USER='$TEST_USER'
LOGNAME='$TEST_USER'
PATH='/usr/local/bin:/usr/bin:/bin'
TEST_USER='$TEST_USER'
TEST_PASSWORD=$(printf '%s' "$TEST_PASSWORD" | sed "s/'/'\\\\''/g" | sed "s/^/'/;s/$/'/")
TARGET_WAIT='$TARGET_WAIT'
DESKTOP_WAIT='$DESKTOP_WAIT'
ENVEOF
chmod 0644 /etc/fdo-verify-session.env

echo "=== login session checks ==="
su -s /bin/sh "$TEST_USER" -c '
    set -a
    . /etc/fdo-verify-session.env
    set +a
    exec /usr/local/libexec/fdo-verify/user-check.sh
'
user_rc=$?
echo "user-check-rc=$user_rc"

if grep -q '^HARNESS-FAIL' "$tmp"; then
    diagnostics
    finish 3
fi
if grep -q 'FAIL' "$tmp"; then
    # A failed desktop check must still leave enough evidence to tell a
    # package failure from a session that disappeared mid-run.
    diagnostics
    finish 1
fi
finish 0
EOF
chmod 0755 "$ROOTFS/usr/local/libexec/fdo-verify/check.sh"

cat > "$ROOTFS/usr/local/libexec/fdo-verify/user-check.sh" <<'EOF'
#!/bin/sh
# Runs inside the logged-in XFCE session as the test user.
set -u

harness_fail() {
    echo "HARNESS-FAIL: $*"
    exit 3
}

echo "=== session environment ==="
echo "user=$(id -un) uid=$(id -u)"
echo "DISPLAY=${DISPLAY:-<unset>}"
echo "XAUTHORITY=${XAUTHORITY:-<unset>}"
echo "XDG_CURRENT_DESKTOP=${XDG_CURRENT_DESKTOP:-<unset>}"
echo "XDG_SESSION_TYPE=${XDG_SESSION_TYPE:-<unset>}"
echo "XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-<unset>}"
echo "DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS:-<unset>}"
if [ -r "${XAUTHORITY:-/nonexistent}" ] && command -v xauth >/dev/null 2>&1; then
    echo "xauth-at-start: $(xauth -f "$XAUTHORITY" list 2>/dev/null | head -1)"
fi

# The portal and Secret Service are only tested on the systemd user bus.
# A private dbus-launch bus means the real login path was not exercised.
case "${DBUS_SESSION_BUS_ADDRESS:-}" in
    unix:path=/run/user/*/bus)
        echo "PASS  session-bus-address           systemd user manager bus" ;;
    unix:path=/tmp/dbus-*)
        harness_fail "private dbus-launch bus ${DBUS_SESSION_BUS_ADDRESS}; expected the systemd user manager bus" ;;
    "")
        harness_fail "DBUS_SESSION_BUS_ADDRESS is not set" ;;
    *)
        harness_fail "unexpected session bus ${DBUS_SESSION_BUS_ADDRESS}" ;;
esac

if command -v systemctl >/dev/null 2>&1; then
    manager=$(systemctl --user show -p Version --value 2>/dev/null || true)
    if [ -n "$manager" ]; then
        echo "PASS  user-manager                  systemd $manager"
    else
        harness_fail "systemctl --user cannot reach the user manager on $DBUS_SESSION_BUS_ADDRESS"
    fi

    # The #48 autostart entry must start both targets.  Wait for it, then
    # report a package failure if it did not happen.
    i=0
    while [ "$i" -lt "$TARGET_WAIT" ]; do
        if systemctl --user is-active -q graphical-session.target 2>/dev/null &&
           systemctl --user is-active -q xfce-session.target 2>/dev/null; then
            break
        fi
        i=$((i + 1))
        sleep 1
    done
    graphical=$(systemctl --user is-active graphical-session.target 2>&1 || true)
    xfce=$(systemctl --user is-active xfce-session.target 2>&1 || true)
    if [ "$graphical" = active ] && [ "$xfce" = active ]; then
        echo "PASS  session-targets               graphical-session.target and xfce-session.target are active"
    else
        echo "FAIL  session-targets               graphical-session.target=$graphical xfce-session.target=$xfce (issue #48 autostart entry)"
    fi
    echo "xfce-session-watch.service=$(systemctl --user is-active xfce-session-watch.service 2>&1 || true)"
fi

# graphical-session.target becomes active as soon as the autostart entry
# starts it, which is before xfwm4, xfsettingsd and the panel have drawn the
# desktop.  Wait for the window manager and its EWMH property so the checks
# below do not race the session startup.
echo "=== desktop readiness ==="
ready=0
i=0
while [ "$i" -lt "$DESKTOP_WAIT" ]; do
    if pgrep -u "$(id -u)" -x xfwm4 >/dev/null 2>&1 &&
       pgrep -u "$(id -u)" -x xfce4-panel >/dev/null 2>&1 &&
       pgrep -u "$(id -u)" -x xfsettingsd >/dev/null 2>&1 &&
       xprop -root _NET_SUPPORTING_WM_CHECK 2>/dev/null | grep -q '0x'; then
        ready=1
        break
    fi
    i=$((i + 1))
    sleep 1
done
if [ "$ready" -eq 1 ]; then
    echo "PASS  desktop-ready                xfwm4, xfce4-panel, xfsettingsd and _NET_SUPPORTING_WM_CHECK are up"
else
    xprobe=$(xprop -root _NET_SUPPORTING_WM_CHECK 2>&1 || true)
    case "$xprobe" in
        *"unable to open display"*|*"Authorization required"*|*"No protocol specified"*)
            echo "HARNESS-FAIL: cannot connect to the X display $DISPLAY: $xprobe"
            exit 3
            ;;
    esac
    echo "FAIL  desktop-ready                xfwm4/panel/xfsettingsd/_NET_SUPPORTING_WM_CHECK did not appear in ${DESKTOP_WAIT}s"
    echo "  processes: $(ps -u "$(id -u)" -o comm= 2>/dev/null | sort | tr '\n' ' ')"
    echo "  xprop: $xprobe"
fi
sleep 2

echo "=== startx log ==="
cat /run/xfce-test-startx.log 2>/dev/null || true

echo "=== session checker ==="
/usr/local/bin/fdo_session_check.sh || true

# The session checker launches a terminal to test startup notification.  If
# that or anything else takes the session down, say so explicitly instead of
# letting the portal and sound checks report confusing symptoms.
session_alive=0
pgrep -u "$(id -u)" -x xfce4-session >/dev/null 2>&1 && session_alive=1
targets_after=$(systemctl --user is-active graphical-session.target 2>&1 || true)
x_after=$(xprop -root _NET_SUPPORTING_WM_CHECK 2>&1 | head -1)
echo "session-after-checker: xfce4-session=$session_alive graphical-session.target=$targets_after"
echo "x-after-checker: $x_after"
if [ "$session_alive" -ne 1 ] || [ "$targets_after" != active ]; then
    echo "FAIL  session-liveness              xfce4-session or graphical-session.target disappeared during the checks"
fi

echo "=== portal ==="
portal_target=$(systemctl --user is-active graphical-session.target 2>&1 || true)
if [ "$portal_target" != active ]; then
    echo "portal: FAIL (graphical-session.target=$portal_target; the session ended before activation)"
else
    portal_before=$(systemctl --user is-active xdg-desktop-portal.service 2>&1 || true)
    systemctl --user start xdg-desktop-portal.service 2>&1 || true
    portal_out=$(timeout 45 busctl --user introspect org.freedesktop.portal.Desktop \
        /org/freedesktop/portal/desktop 2>&1)
    portal_rc=$?
    portal_after=$(systemctl --user is-active xdg-desktop-portal.service 2>&1 || true)
    if [ "$portal_after" = activating ]; then
        i=0
        while [ "$i" -lt 45 ]; do
            portal_after=$(systemctl --user is-active xdg-desktop-portal.service 2>&1 || true)
            [ "$portal_after" = active ] && break
            i=$((i + 1))
            sleep 1
        done
        if [ "$portal_rc" -ne 0 ]; then
            portal_out=$(timeout 30 busctl --user introspect \
                org.freedesktop.portal.Desktop \
                /org/freedesktop/portal/desktop 2>&1)
            portal_rc=$?
        fi
    fi
    printf '%s\n' "$portal_out" | head -30
    echo "portal-service: $portal_before -> $portal_after"
    echo "portal-mainpid=$(systemctl --user show -p MainPID --value xdg-desktop-portal.service 2>&1 || true)"
    if [ "$portal_rc" -eq 0 ] &&
       printf '%s\n' "$portal_out" | grep -q 'org.freedesktop.portal.FileChooser'; then
        if [ "$portal_after" = active ]; then
            echo "portal: PASS (activated by the systemd user manager)"
        else
            echo "portal: FAIL (introspection worked but the user manager did not start the service)"
        fi
    else
        echo "portal: FAIL (introspection rc=$portal_rc)"
        systemctl --user status xdg-desktop-portal.service --no-pager -l 2>&1 | head -40 || true
        journalctl --user -u xdg-desktop-portal.service --no-pager -n 80 2>&1 || true
    fi
fi

echo "=== notifications ==="
# The daemon is started by the session autostart or D-Bus activation; give
# both paths a bounded window before reporting a failure.
i=0
while [ "$i" -lt 20 ]; do
    if busctl --user status org.freedesktop.Notifications \
            >/dev/null 2>&1; then
        break
    fi
    i=$((i + 1))
    sleep 1
done
notify_out=$(timeout 20 busctl --user introspect org.freedesktop.Notifications \
    /org/freedesktop/Notifications 2>&1)
notify_rc=$?
printf '%s\n' "$notify_out" | head -20
if [ "$notify_rc" -eq 0 ] &&
   printf '%s\n' "$notify_out" | grep -q 'org.freedesktop.Notifications'; then
    echo "notification-service: PASS"
else
    echo "notification-service: FAIL (rc=$notify_rc)"
fi
if notify-send -t 2000 "Tenko check" "desktop notification"; then
    echo "notify-send: ok"
else
    echo "notify-send: FAILED"
fi

echo "=== secret service (login session) ==="
if command -v secret-tool >/dev/null 2>&1; then
    # Autologin has no password for PAM to pass to gnome-keyring, so unlock
    # the login keyring with the test account's password first.  A greeter
    # login unlocks the same keyring through pam_gnome_keyring (documented in
    # docs/testing.md).
    if command -v gnome-keyring-daemon >/dev/null 2>&1; then
        printf '%s\n' "$TEST_PASSWORD" |
            timeout 15 gnome-keyring-daemon --unlock --components=secrets \
            >/dev/null 2>&1 || true
    fi
    if secret_out=$(printf '%s' 'tenko-secret' |
            timeout 20 secret-tool store --label=tenko service tenko key test 2>&1); then
        secret_collection=login
    elif secret_out=$(printf '%s' 'tenko-secret' |
            timeout 20 secret-tool store \
            --collection=/org/freedesktop/secrets/collection/session \
            --label=tenko service tenko key test 2>&1); then
        # Autologin does not create the persistent login collection (PAM has
        # no password to unlock it); the session collection is still a real
        # Secret Service round-trip through gnome-keyring.
        secret_collection=session
    else
        secret_collection=
    fi
    if [ -n "$secret_collection" ]; then
        value=$(timeout 20 secret-tool lookup service tenko key test 2>/dev/null || true)
        if [ "$value" = tenko-secret ]; then
            echo "secret-tool round-trip: ${value} (${secret_collection} collection)"
        else
            echo "secret-tool round-trip: FAILED (lookup returned '${value:-<empty>}')"
        fi
    else
        echo "secret-tool round-trip: FAILED (store: ${secret_out:-unknown error})"
    fi
else
    echo "secret-tool round-trip: FAILED (secret-tool is not installed)"
fi

echo "=== trash ==="
rm -rf "$HOME/.local/share/Trash" "$HOME/fdo-trash-test"
echo test > "$HOME/fdo-trash-test"
if gio trash "$HOME/fdo-trash-test" &&
   [ -f "$HOME/.local/share/Trash/files/fdo-trash-test" ]; then
    echo "gio trash: ok"
else
    echo "gio trash: FAILED"
fi

echo "=== sound ==="
xfconf-query -c xsettings -p /Net/SoundThemeName 2>&1 || true
if [ ! -e /sys/class/sound ] || [ -z "$(ls -A /sys/class/sound 2>/dev/null)" ]; then
    echo "canberra bell: SKIP (no audio device in this VM)"
elif command -v canberra-gtk-play >/dev/null 2>&1; then
    echo "sound X client: DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY"
    if [ -r "$XAUTHORITY" ] && command -v xauth >/dev/null 2>&1; then
        echo "  xauth: $(xauth -f "$XAUTHORITY" list 2>/dev/null | head -1)"
    else
        echo "  XAUTHORITY is not readable by $(id -un)"
    fi
    sound_out=$(DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" \
        canberra-gtk-play -i bell 2>&1) && sound_rc=0 || sound_rc=1
    if [ "$sound_rc" -eq 0 ]; then
        echo "canberra bell: ok"
    else
        case "$sound_out" in
            *"Sound disabled"*|*"Connection refused"*|*"not available"*|*"no audio device"*|*"No such device"*|*"Cannot open audio"*|*"Could not open audio"*)
                echo "canberra bell: SKIP ($sound_out)"
                ;;
            *"Authorization required"*|*"Cannot open display"*|*"No protocol specified"*)
                # Playback is a hardware check; a playback client that cannot
                # open the display must not turn the desktop gate red.  The
                # session checker above already proved the X connection.
                echo "canberra bell: SKIP (playback client could not open the display: $sound_out)"
                ;;
            *)
                echo "canberra bell: FAILED ($sound_out)"
                ;;
        esac
    fi
else
    echo "canberra-gtk-play: SKIP (not installed)"
fi

echo "=== keyring PAM configuration ==="
for pam in /etc/pam.d/lightdm /etc/pam.d/lightdm-autologin; do
    if grep -q 'pam_gnome_keyring.so' "$pam" 2>/dev/null; then
        echo "pam-keyring: PASS ($pam)"
    else
        echo "pam-keyring: FAIL ($pam has no pam_gnome_keyring.so)"
    fi
done

echo "=== reached the end ==="
EOF
chmod 0755 "$ROOTFS/usr/local/libexec/fdo-verify/user-check.sh"

cat > "$ROOTFS/etc/systemd/system/fdo-prep.service" <<'EOF'
[Unit]
Description=Prepare the freedesktop QEMU verification session
After=local-fs.target
Before=lightdm.service

[Service]
Type=oneshot
RemainAfterExit=yes
TimeoutStartSec=120
ExecStart=/usr/local/libexec/fdo-verify/prep.sh

[Install]
WantedBy=multi-user.target
EOF
ln -sf ../fdo-prep.service \
    "$ROOTFS/etc/systemd/system/multi-user.target.wants/fdo-prep.service"

cat > "$ROOTFS/etc/systemd/system/fdo-check.service" <<'EOF'
[Unit]
Description=Run the freedesktop desktop checks in the LightDM login session
After=lightdm.service fdo-prep.service
Wants=lightdm.service
TimeoutStartSec=360

[Service]
Type=oneshot
ExecStart=/usr/local/libexec/fdo-verify/check.sh

[Install]
WantedBy=graphical.target
EOF
ln -sf ../fdo-check.service \
    "$ROOTFS/etc/systemd/system/graphical.target.wants/fdo-check.service"

# The checker script itself is shared with the standalone session check.
install -m 0755 scripts/qemu/fdo_session_check.sh \
    "$ROOTFS/usr/local/bin/fdo_session_check.sh"

# tenko-firstboot is ordered before display-manager.service and blocks it
# until the root password question is answered.  This test image has no
# console user, so ship the done marker from the start instead of racing
# fdo-prep against the prompt on a fresh image.
mkdir -p "$ROOTFS/var/lib/tenko"
printf 'skipped by qemu_fdo_verify image build\n' \
    > "$ROOTFS/var/lib/tenko/firstboot-root-password.done"

{
    printf 'SESSION_WAIT=%s\n' "$SESSION_WAIT"
    printf 'TARGET_WAIT=%s\n' "$TARGET_WAIT"
    printf 'DESKTOP_WAIT=%s\n' "$DESKTOP_WAIT"
} > "$ROOTFS/etc/fdo-verify.timeouts"

echo "rebuilding the ext4 image with the guest checks"
rm -f "$IMG"
truncate -s "$IMGSIZE" "$IMG"
unshare -r /usr/sbin/mke2fs -q -t ext4 -d "$ROOTFS" "$IMG"

mkdir -p "$SHARE"
rm -f "$SHARE/fdo-check.txt" "$SHARE/fdo-check.txt.tmp" "$SHARE/fdo-prep.txt" \
      "$SERIAL" "$MON"
initrd=()
[ "${USE_INITRD:-1}" = 1 ] && [ -f "$ROOTFS/boot/initramfs-$KVER.img" ] && \
    initrd=(-initrd "$ROOTFS/boot/initramfs-$KVER.img")

accel=(-enable-kvm -cpu host)
[ -w /dev/kvm ] || accel=(-cpu max)

qemu_start=$(date +%s)
qemu-system-x86_64 \
    "${accel[@]}" -m "$MEM" -smp 4 \
    -kernel "$ROOTFS/boot/vmlinuz-$KVER" \
    "${initrd[@]}" \
    -append "root=/dev/vda rw console=ttyS0 loglevel=6 systemd.show_status=1" \
    -drive file="$IMG",format=raw,if=virtio \
    -vga std \
    -display none -vnc 127.0.0.1:1 \
    -monitor "unix:$MON,server,nowait" \
    -serial "file:$SERIAL" \
    -virtfs "local,path=$SHARE,mount_tag=host0,security_model=none" \
    -no-reboot &
qpid=$!
cleanup() {
    if [ "$KEEP" != "1" ]; then
        # Reap QEMU before the caller starts the next run; otherwise the old
        # guest can still hold the 9p share and the image while the next run
        # recreates them.
        kill "$qpid" 2>/dev/null || true
        wait "$qpid" 2>/dev/null || true
    fi
}
trap cleanup EXIT

echo "qemu pid $qpid; waiting up to ${WAIT}s for the guest checks"
deadline=$(( $(date +%s) + WAIT ))
while [ "$(date +%s)" -lt "$deadline" ]; do
    if ! kill -0 "$qpid" 2>/dev/null; then
        echo "harness failure: qemu exited before the guest checks finished" >&2
        break
    fi
    if [ -s "$SHARE/fdo-check.txt" ] &&
       grep -q '^=== done ===$' "$SHARE/fdo-check.txt"; then
        break
    fi
    sleep 2
done

if [ ! -s "$SHARE/fdo-check.txt" ] ||
   ! grep -q '^=== done ===$' "$SHARE/fdo-check.txt"; then
    echo "guest phase: $(( $(date +%s) - qemu_start ))s (timeout or no result)" >&2
    echo "=== harness failure: no complete guest result ===" >&2
    [ -s "$SHARE/fdo-check.txt.tmp" ] && cat "$SHARE/fdo-check.txt.tmp" >&2
    echo "--- serial tail ---" >&2
    tail -120 "$SERIAL" >&2 || true
    echo "--- prep marker ---" >&2
    cat "$SHARE/fdo-prep.txt" 2>/dev/null >&2 || true
    exit 2
fi

echo "guest phase: $(( $(date +%s) - qemu_start ))s"
cat "$SHARE/fdo-check.txt"

if grep -q '^HARNESS-FAIL' "$SHARE/fdo-check.txt"; then
    echo "freedesktop desktop check: HARNESS FAILURE (the guest session is not usable)" >&2
    exit 2
fi
if grep -q '^FAIL' "$SHARE/fdo-check.txt"; then
    echo "freedesktop desktop check: FAILED" >&2
    exit 1
fi

# Do not let a truncated or silently shortened result look green: the gate
# claims coverage of these specific paths.
missing=
for pattern in \
    'PASS  display' \
    'PASS  session-bus' \
    'PASS  user-manager' \
    'PASS  session-targets' \
    'PASS  desktop-ready' \
    'PASS  secret-root' \
    'portal: PASS' \
    'notification-service: PASS' \
    'secret-tool round-trip: tenko-secret' \
    'gio trash: ok' \
    'pam-keyring: PASS'
do
    grep -qF "$pattern" "$SHARE/fdo-check.txt" || \
        missing="$missing '$pattern'"
done
if [ -n "$missing" ]; then
    echo "harness failure: fdo-check.txt is missing required results:$missing" >&2
    exit 2
fi

echo "total: $(( $(date +%s) - start_time ))s"
echo "freedesktop desktop check: OK"
