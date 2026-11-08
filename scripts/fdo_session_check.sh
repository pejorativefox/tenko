#!/bin/sh
# Check the freedesktop session protocols in a live XFCE/X11 session.
#
# The check is network-free and read-only: it only queries X properties,
# the user session bus and the dynamic linker cache.  It prints one
# PASS/FAIL/SKIP line per check and exits non-zero only when a check fails.
# Missing optional tools are reported as SKIP; a missing DISPLAY or session
# bus is a failure because the checker is meant to run inside the desktop
# session (for example from the graphical QEMU test after login).
#
# Tenko relies on a systemd user manager for D-Bus activation: a private
# dbus-launch bus (unix:path=/tmp/dbus-*) cannot activate services such as
# xdg-desktop-portal.  The checker therefore requires the manager bus and
# the issue #48 session targets, not merely "some bus".
#
# Usage:
#   sh scripts/fdo_session_check.sh
#
set -u

status=0

pass() {
    printf 'PASS  %-28s %s\n' "$1" "$2"
}

fail() {
    printf 'FAIL  %-28s %s\n' "$1" "$2"
    status=1
}

skip() {
    printf 'SKIP  %-28s %s\n' "$1" "$2"
}

have() {
    command -v "$1" >/dev/null 2>&1
}

# ---------------------------------------------------------------------------
# Session environment
# ---------------------------------------------------------------------------
env_ok=1

if [ -n "${DISPLAY:-}" ]; then
    pass "display" "DISPLAY=$DISPLAY"
else
    fail "display" "DISPLAY is not set; run this inside the X session"
    env_ok=0
fi

if [ -z "${DBUS_SESSION_BUS_ADDRESS:-}" ]; then
    fail "session-bus" "DBUS_SESSION_BUS_ADDRESS is not set; LightDM/startxfce4 must provide a session bus"
    env_ok=0
elif have busctl; then
    if busctl --user status >/dev/null 2>&1; then
        case "$DBUS_SESSION_BUS_ADDRESS" in
            unix:path=/tmp/dbus-*)
                fail "session-bus" "private dbus-launch bus; the systemd user manager bus is required for portal activation"
                env_ok=0
                ;;
            *)
                pass "session-bus" "busctl --user status succeeds ($DBUS_SESSION_BUS_ADDRESS)"
                ;;
        esac
    else
        fail "session-bus" "DBUS_SESSION_BUS_ADDRESS is set but busctl --user status failed"
        env_ok=0
    fi
elif have dbus-send; then
    if dbus-send --session --print-reply --dest=org.freedesktop.DBus \
        / org.freedesktop.DBus.GetId >/dev/null 2>&1; then
        case "$DBUS_SESSION_BUS_ADDRESS" in
            unix:path=/tmp/dbus-*)
                fail "session-bus" "private dbus-launch bus; the systemd user manager bus is required for portal activation"
                env_ok=0
                ;;
            *)
                pass "session-bus" "org.freedesktop.DBus answers on the session bus"
                ;;
        esac
    else
        fail "session-bus" "DBUS_SESSION_BUS_ADDRESS is set but dbus-send could not reach the bus"
        env_ok=0
    fi
else
    skip "session-bus" "DBUS_SESSION_BUS_ADDRESS is set but neither busctl nor dbus-send is installed"
fi

if [ "$env_ok" -ne 1 ]; then
    printf '%s\n' "session integration: no usable X/session-bus environment" >&2
    exit "$status"
fi

# ---------------------------------------------------------------------------
# Systemd user manager and the #48 session targets
#
# The portal is a D-Bus activated user service with
# Requisite=graphical-session.target.  Without the user manager and the
# targets, introspection can still succeed through the legacy Exec= path on
# a private bus, which is not the path a real login uses.
# ---------------------------------------------------------------------------
if ! have systemctl; then
    skip "user-manager" "systemctl is not installed; cannot verify systemd user services"
    skip "session-targets" "systemctl is not installed"
else
    manager=$(systemctl --user show -p Version --value 2>/dev/null) || manager=
    if [ -n "$manager" ]; then
        pass "user-manager" "systemd user manager $manager"
    else
        fail "user-manager" "systemctl --user cannot reach the user manager"
    fi
    if [ -n "$manager" ]; then
        i=0
        while [ "$i" -lt 20 ]; do
            if systemctl --user is-active -q graphical-session.target 2>/dev/null &&
               systemctl --user is-active -q xfce-session.target 2>/dev/null; then
                break
            fi
            i=$((i + 1))
            sleep 1
        done
        graphical=$(systemctl --user is-active graphical-session.target 2>&1) ||
            graphical=
        xfce=$(systemctl --user is-active xfce-session.target 2>&1) || xfce=
        if [ "$graphical" = active ] && [ "$xfce" = active ]; then
            pass "session-targets" "graphical-session.target and xfce-session.target are active"
        else
            fail "session-targets" "graphical-session.target=${graphical:-unknown} xfce-session.target=${xfce:-unknown}"
        fi
    fi
fi

# ---------------------------------------------------------------------------
# EWMH (Window Manager 1.5)
# ---------------------------------------------------------------------------
if ! have xprop; then
    skip "ewmh-atoms" "xprop not installed; cannot inspect root window properties"
    skip "ewmh-supported" "xprop not installed"
    skip "ewmh-wm-check" "xprop not installed"
else
    missing=
    for atom in _NET_SUPPORTING_WM_CHECK _NET_SUPPORTED \
                _NET_CLIENT_LIST _NET_ACTIVE_WINDOW; do
        value=$(xprop -root "$atom" 2>/dev/null) || value=
        case "$value" in
            ""|*"not found"*|*"no such atom"*)
                missing="$missing $atom"
                ;;
        esac
    done

    if [ -n "$missing" ]; then
        fail "ewmh-atoms" "missing root properties:$missing"
    else
        pass "ewmh-atoms" "_NET_SUPPORTING_WM_CHECK, _NET_SUPPORTED, _NET_CLIENT_LIST and _NET_ACTIVE_WINDOW are present"
    fi

    supported=$(xprop -root _NET_SUPPORTED 2>/dev/null) || supported=
    unsupported=
    for atom in _NET_SUPPORTING_WM_CHECK _NET_SUPPORTED \
                _NET_CLIENT_LIST _NET_ACTIVE_WINDOW; do
        printf '%s\n' "$supported" | grep -q "$atom" ||
            unsupported="$unsupported $atom"
    done
    if [ -n "$unsupported" ]; then
        fail "ewmh-supported" "not advertised in _NET_SUPPORTED:$unsupported"
    else
        pass "ewmh-supported" "the required atoms are advertised in _NET_SUPPORTED"
    fi

    wm_check=$(xprop -root _NET_SUPPORTING_WM_CHECK 2>/dev/null) || wm_check=
    wm_win=$(printf '%s\n' "$wm_check" |
        sed -n 's/.*# \(0x[0-9a-fA-F][0-9a-fA-F]*\).*/\1/p')
    if [ -z "$wm_win" ]; then
        fail "ewmh-wm-check" "_NET_SUPPORTING_WM_CHECK does not name a window"
    else
        wm_name=$(xprop -id "$wm_win" _NET_WM_NAME 2>/dev/null) || wm_name=
        case "$wm_name" in
            ""|*"not found"*|*"no such atom"*)
                fail "ewmh-wm-check" "window $wm_win has no _NET_WM_NAME"
                ;;
            *)
                pass "ewmh-wm-check" "_NET_SUPPORTING_WM_CHECK=$wm_win ($wm_name)"
                ;;
        esac
    fi
fi

# ---------------------------------------------------------------------------
# XSettings 0.5
#
# xprop cannot query X selection owners, so first try the root property (some
# servers expose it), then XGetSelectionOwner through libX11 when python3 is
# available.  When the owner still cannot be read, report SKIP rather than a
# false failure.
# ---------------------------------------------------------------------------
read_xsettings_owner() {
    owner=$(xprop -root _XSETTINGS_S0 2>/dev/null) || owner=
    case "$owner" in
        ""|*"not found"*|*"no such atom"*) ;;
        *)
            printf '%s\n' "$owner" |
                sed -n 's/.*# \(0x[0-9a-fA-F][0-9a-fA-F]*\).*/\1/p'
            return 0
            ;;
    esac

    if ! have python3; then
        return 0
    fi
    python3 -c '
import ctypes
import sys
try:
    lib = ctypes.CDLL("libX11.so.6")
except OSError:
    sys.exit(1)
lib.XOpenDisplay.restype = ctypes.c_void_p
lib.XInternAtom.restype = ctypes.c_ulong
lib.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
lib.XGetSelectionOwner.restype = ctypes.c_ulong
lib.XGetSelectionOwner.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
lib.XCloseDisplay.argtypes = [ctypes.c_void_p]
display = lib.XOpenDisplay(None)
if not display:
    sys.exit(1)
try:
    atom = lib.XInternAtom(display, b"_XSETTINGS_S0", 0)
    owner = lib.XGetSelectionOwner(display, atom)
finally:
    lib.XCloseDisplay(display)
if owner:
    print("0x%x" % owner)
' 2>/dev/null || :
}

if ! have xprop; then
    skip "xsettings" "xprop not installed; cannot inspect the _XSETTINGS_S0 selection owner"
else
    owner_win=$(read_xsettings_owner)
    if [ -z "$owner_win" ]; then
        if have xfconf-query &&
            xfconf-query -c xsettings -p /Net/ThemeName >/dev/null 2>&1; then
            skip "xsettings" "xfconf xsettings channel responds, but the _XSETTINGS_S0 selection owner could not be read"
        else
            skip "xsettings" "the _XSETTINGS_S0 selection owner could not be read; is an XSettings manager running?"
        fi
    else
        settings=$(xprop -id "$owner_win" _XSETTINGS_SETTINGS 2>/dev/null) ||
            settings=
        case "$settings" in
            ""|*"not found"*|*"no such atom"*)
                fail "xsettings" "_XSETTINGS_S0 owner $owner_win has no _XSETTINGS_SETTINGS property"
                ;;
            *)
                pass "xsettings" "_XSETTINGS_S0 owned by $owner_win with _XSETTINGS_SETTINGS"
                ;;
        esac
    fi
fi

# ---------------------------------------------------------------------------
# Startup Notification 0.2
# ---------------------------------------------------------------------------
ldconfig_bin=
if have ldconfig; then
    ldconfig_bin=$(command -v ldconfig)
elif [ -x /sbin/ldconfig ]; then
    ldconfig_bin=/sbin/ldconfig
elif [ -x /usr/sbin/ldconfig ]; then
    ldconfig_bin=/usr/sbin/ldconfig
fi

if [ -z "$ldconfig_bin" ]; then
    skip "startup-lib" "ldconfig not available; cannot inspect the loader cache"
elif "$ldconfig_bin" -p 2>/dev/null | grep -q 'libstartup-notification'; then
    pass "startup-lib" "libstartup-notification is in the loader cache"
else
    fail "startup-lib" "libstartup-notification is not in the loader cache"
fi

if ! have xprop; then
    skip "startup-e2e" "xprop not installed; cannot look for _NET_STARTUP_ID"
elif ! have xwininfo; then
    skip "startup-e2e" "xwininfo not installed; cannot search all X windows for _NET_STARTUP_ID"
elif have xfce4-terminal; then
    startup_token="tenko-session-check-$$-$(date +%s)"
    startup_log=/tmp/tenko-startup-check.$$.log
    DESKTOP_STARTUP_ID="$startup_token" \
        xfce4-terminal --disable-server --title=tenko-startup-check \
        >"$startup_log" 2>&1 &
    startup_pid=$!
    startup_found=0
    startup_tries=0
    while [ "$startup_tries" -lt 10 ]; do
        sleep 1
        startup_tries=$((startup_tries + 1))
        # The startup id is usually on the application's leader window,
        # which is not necessarily in _NET_CLIENT_LIST, so walk the tree.
        windows=$(xwininfo -root -tree 2>/dev/null |
            sed -n 's/^ *\(0x[0-9a-fA-F][0-9a-fA-F]*\).*/\1/p')
        for win in $windows; do
            [ -n "$win" ] || continue
            prop=$(xprop -id "$win" _NET_STARTUP_ID 2>/dev/null) || prop=
            case "$prop" in
                *"$startup_token"*)
                    startup_found=1
                    break
                    ;;
            esac
        done
        [ "$startup_found" -eq 1 ] && break
    done
    # Only kill the process if the PID still belongs to the terminal; the
    # application may have exited and its PID may have been reused.
    if [ "$(ps -o comm= -p "$startup_pid" 2>/dev/null)" = xfce4-terminal ]; then
        kill "$startup_pid" 2>/dev/null || :
    fi
    wait "$startup_pid" 2>/dev/null || :
    startup_err=$(sed -n '1p' "$startup_log" 2>/dev/null) || startup_err=
    rm -f "$startup_log"
    if [ "$startup_found" -eq 1 ]; then
        pass "startup-e2e" "xfce4-terminal published _NET_STARTUP_ID=$startup_token"
    else
        fail "startup-e2e" "xfce4-terminal did not publish _NET_STARTUP_ID in 10s${startup_err:+ ($startup_err)}"
    fi
else
    skip "startup-e2e" "no test application with startup-notification support (xfce4-terminal) is installed"
fi

# ---------------------------------------------------------------------------
# System tray (System Tray 0.3 / XEmbed 0.5) and StatusNotifierItem
# ---------------------------------------------------------------------------
if ! have python3; then
    skip "tray-selection" "python3 not installed; cannot query _NET_SYSTEM_TRAY_S0"
elif ! python3 -c 'import ctypes' >/dev/null 2>&1; then
    skip "tray-selection" "python3 ctypes is unavailable"
else
    python3 - <<'PY' 2>/dev/null
import ctypes
import sys

try:
    xlib = ctypes.CDLL("libX11.so.6")
except OSError:
    sys.exit(2)
xlib.XOpenDisplay.restype = ctypes.c_void_p
display = xlib.XOpenDisplay(None)
if not display:
    # libX11 loaded but the display could not be opened.
    sys.exit(3)
xlib.XInternAtom.restype = ctypes.c_ulong
xlib.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
xlib.XGetSelectionOwner.restype = ctypes.c_ulong
xlib.XGetSelectionOwner.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
atom = xlib.XInternAtom(display, b"_NET_SYSTEM_TRAY_S0", 0)
owner = xlib.XGetSelectionOwner(display, atom)
if owner:
    print(hex(owner))
    sys.exit(0)
sys.exit(1)
PY
    tray_rc=$?
    case "$tray_rc" in
        0)  pass "tray-selection" "_NET_SYSTEM_TRAY_S0 has an owner" ;;
        1)  fail "tray-selection" "no XEmbed system tray owns _NET_SYSTEM_TRAY_S0" ;;
        2)  skip "tray-selection" "libX11 is unavailable; cannot query the tray selection" ;;
        3)  fail "tray-selection" "the X display is not reachable; cannot query the tray selection" ;;
        *)  skip "tray-selection" "libX11 returned $tray_rc; cannot query the tray selection" ;;
    esac
fi

if ! have xfconf-query; then
    skip "tray-plugin" "xfconf-query not installed; cannot inspect the panel plugins"
else
    plugins=$(xfconf-query -c xfce4-panel -p /plugins -l -v 2>/dev/null) ||
        plugins=$(xfconf-query -c xfce4-panel -p /plugins 2>/dev/null) ||
        plugins=
    if printf '%s\n' "$plugins" | grep -q 'systray'; then
        pass "tray-plugin" "the panel configuration includes the systray plugin"
    else
        fail "tray-plugin" "the panel configuration has no systray plugin"
    fi
    if printf '%s\n' "$plugins" | grep -q 'statusnotifier'; then
        pass "sni-host" "the panel configuration includes a StatusNotifierItem host"
    else
        skip "sni-host" "no StatusNotifierItem host is shipped (draft; documented)"
    fi
fi

if [ "$status" -eq 0 ]; then
    printf '%s\n' "session integration: OK"
else
    printf '%s\n' "session integration: FAILED" >&2
fi
exit "$status"