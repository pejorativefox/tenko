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

# Wait for the login session itself.  The session targets are checked by
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
