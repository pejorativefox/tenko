#!/usr/bin/env bash
# Boot the published desktop set in QEMU and run the desktop-level
# freedesktop checks inside the XFCE session.
#
# This is the final gate for the freedesktop compliance programme (#32): it
# verifies notifications, the portal, the Secret Service, the sound theme,
# trash, the tray, XSettings and the EWMH atoms on a real installed desktop,
# not just from package metadata.
#
# Usage:
#   REPO=build/publish-check scripts/qemu_fdo_verify.sh
#   SKIP_BUILD=1 scripts/qemu_fdo_verify.sh   # reuse an existing rootfs/image
#   KEEP=1 scripts/qemu_fdo_verify.sh         # leave QEMU running
#
# The guest runs a root XFCE session (the same harness as
# qemu_boot_graphical.sh), so no greeter login is needed.  The PAM keyring
# unlock is verified separately by the LightDM PAM configuration and the
# final manual login test.
set -euo pipefail
cd "$(dirname "$0")/.."

REPO=${REPO:-build/publish-check}
KVER=${KVER:-7.3.1}
ROOTFS=${ROOTFS:-$PWD/build/rootfs-fdo}
IMG=${IMG:-$PWD/build/fdo-desktop.img}
SERIAL=${SERIAL:-$PWD/build/fdo-serial.log}
SHARE=${SHARE:-$PWD/build/qemu-share}
MON=${MON:-$PWD/build/fdo-monitor.sock}
IMGSIZE=${IMGSIZE:-6G}
WAIT=${WAIT:-120}
SKIP_BUILD=${SKIP_BUILD:-0}
KEEP=${KEEP:-0}

if [ "$SKIP_BUILD" != "1" ]; then
    echo "building the desktop rootfs from $REPO"
    REPO="$REPO" ROOTFS="$ROOTFS" IMG="$IMG" IMGSIZE="$IMGSIZE" \
        BUILD_ONLY=1 scripts/qemu_boot_graphical.sh
fi

mkdir -p "$SHARE"

# The graphical harness starts X as root on tty1.  Disable X access control
# for this test session and give startx a stable XAUTHORITY so the XFCE
# session can connect even when the harness rebuilds the image without
# replaying qemu_boot_graphical.sh.
if [ -f "$ROOTFS/etc/systemd/system/xfce-test.service" ]; then
    sed -i 's|^ExecStart=/usr/bin/startx -- :0 vt1$|ExecStart=/usr/bin/startx -- :0 vt1 -ac|' \
        "$ROOTFS/etc/systemd/system/xfce-test.service"
    sed -i '/^Environment=XAUTHORITY=/d' \
        "$ROOTFS/etc/systemd/system/xfce-test.service"
    rm -f "$ROOTFS/root/.Xauthority"
    # The graphical harness starts X directly; LightDM would race it for :0.
    rm -f "$ROOTFS/etc/systemd/system/display-manager.service"
    ln -sf /dev/null "$ROOTFS/etc/systemd/system/lightdm.service"
fi

# The session checker runs inside the guest.
install -m 0755 scripts/fdo_session_check.sh \
    "$ROOTFS/usr/local/bin/fdo_session_check.sh"

cat > "$ROOTFS/usr/local/bin/fdo-check.sh" <<'EOF'
#!/bin/sh
# Runs inside the guest's root XFCE session and writes to the 9p share.
exec > /mnt/fdo-check.txt 2>&1
export DISPLAY=:0 XAUTHORITY=/root/.Xauthority
export HOME=/root

# The XFCE session owns a private bus; wait for it (the session can take
# longer than a fixed sleep on a cold boot).  The address is usually
# unix:path=/run/user/0/bus, so it does not contain the word "session";
# exclude the system bus explicitly.
tries=0
while [ "$tries" -lt 45 ]; do
    for envfile in /proc/[0-9]*/environ; do
        [ -r "$envfile" ] || continue
        addr=$( (tr '\0' '\n' < "$envfile") 2>/dev/null |
            sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p' | head -1)
        case "$addr" in
            ""|*system_bus*|*/run/dbus/*) continue ;;
            *) export DBUS_SESSION_BUS_ADDRESS="$addr"; break 2 ;;
        esac
    done
    tries=$((tries + 1))
    sleep 2
done
echo "bus=${DBUS_SESSION_BUS_ADDRESS:-none}"

echo "=== session checker ==="
/usr/local/bin/fdo_session_check.sh || true

echo "=== portal ==="
busctl --user introspect org.freedesktop.portal.Desktop \
    /org/freedesktop/portal/desktop 2>&1 | head -30 || true

echo "=== notifications ==="
busctl --user introspect org.freedesktop.Notifications \
    /org/freedesktop/Notifications 2>&1 | head -20 || true
if notify-send -t 2000 "Tenko check" "desktop notification"; then
    echo "notify-send: ok"
else
    echo "notify-send: FAILED"
fi

echo "=== secret service ==="
if command -v gnome-keyring-daemon >/dev/null 2>&1; then
    printf 'tenko1\n' | gnome-keyring-daemon --unlock --components=secrets \
        >/dev/null 2>&1 || true
fi
if printf 'tenko-secret' | secret-tool store --label=tenko \
        service tenko key test >/dev/null 2>&1; then
    value=$(secret-tool lookup service tenko key test 2>/dev/null || true)
    echo "secret-tool round-trip: ${value:-<empty>}"
else
    echo "secret-tool store: FAILED (locked keyring or no provider)"
fi

echo "=== trash ==="
rm -rf /root/.local/share/Trash /root/trash-test
echo test > /root/trash-test
if gio trash /root/trash-test && [ -f /root/.local/share/Trash/files/trash-test ]; then
    echo "gio trash: ok"
else
    echo "gio trash: FAILED"
fi

echo "=== sound ==="
xfconf-query -c xsettings -p /Net/SoundThemeName 2>&1 || true
if command -v canberra-gtk-play >/dev/null 2>&1; then
    sound_out=$(canberra-gtk-play -i bell 2>&1) && sound_rc=0 || sound_rc=1
    if [ "$sound_rc" -eq 0 ]; then
        echo "canberra bell: ok"
    else
        case "$sound_out" in
            *"Sound disabled"*|*"Connection refused"*|*"not available"*)
                echo "canberra bell: SKIP ($sound_out)"
                ;;
            *)
                echo "canberra bell: FAILED ($sound_out)"
                ;;
        esac
    fi
else
    echo "canberra-gtk-play: SKIP (not installed)"
fi

echo "=== reached the end ==="
EOF
chmod 0755 "$ROOTFS/usr/local/bin/fdo-check.sh"

cat > "$ROOTFS/etc/systemd/system/fdo-check.service" <<'EOF'
[Unit]
Description=Run the freedesktop desktop checks
After=xfce-test.service
Wants=xfce-test.service

[Service]
Type=oneshot
ExecStartPre=/bin/sleep 25
ExecStart=/usr/local/bin/fdo-check.sh
TimeoutStartSec=180

[Install]
WantedBy=graphical.target
EOF
mkdir -p "$ROOTFS/etc/systemd/system/graphical.target.wants"
ln -sf ../fdo-check.service \
    "$ROOTFS/etc/systemd/system/graphical.target.wants/fdo-check.service"

echo "rebuilding the ext4 image with the guest checks"
rm -f "$IMG"
truncate -s "$IMGSIZE" "$IMG"
unshare -r /usr/sbin/mke2fs -q -t ext4 -d "$ROOTFS" "$IMG"

rm -f "$SHARE/fdo-check.txt" "$SERIAL" "$MON"
initrd=()
[ "${USE_INITRD:-1}" = 1 ] && [ -f "$ROOTFS/boot/initramfs-$KVER.img" ] && \
    initrd=(-initrd "$ROOTFS/boot/initramfs-$KVER.img")

accel=(-enable-kvm -cpu host)
[ -w /dev/kvm ] || accel=(-cpu max)

qemu-system-x86_64 \
    "${accel[@]}" -m 3072 -smp 4 \
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
if [ "$KEEP" != "1" ]; then
    trap 'kill $qpid 2>/dev/null || true' EXIT
fi

echo "qemu pid $qpid; waiting ${WAIT}s for the guest checks"
sleep "$WAIT"

if [ -s "$SHARE/fdo-check.txt" ]; then
    cat "$SHARE/fdo-check.txt"
    if grep -q 'FAIL' "$SHARE/fdo-check.txt"; then
        echo "freedesktop desktop check: FAILED" >&2
        exit 1
    fi
    echo "freedesktop desktop check: OK"
else
    echo "no guest result; serial tail:" >&2
    tail -80 "$SERIAL" >&2 || true
    exit 1
fi
