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

    # The xfce-graphical-session autostart entry must start both targets.  Wait for it, then
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
        echo "FAIL  session-targets               graphical-session.target=$graphical xfce-session.target=$xfce (xfce-graphical-session autostart entry)"
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
