#!/usr/bin/env bash
# Boot the installer ISO in QEMU (UEFI/OVMF) and capture the screen.
#
# The disk is blank: the installer should offer it in the disk list and let
# you create a GPT.  Serial output goes to build/installer-serial.log.
set -euo pipefail
cd "$(dirname "$0")/.."

ISO=${ISO:-$PWD/build/tenko-installer.iso}
DISK=${DISK:-$PWD/build/installer-test.img}
DISKSIZE=${DISKSIZE:-20G}
SERIAL=${SERIAL:-$PWD/build/installer-serial.log}
MON=${MON:-$PWD/build/installer-monitor.sock}
SHOT=${SHOT:-$PWD/build/installer-screen.png}
WAIT=${WAIT:-90}
MEM=${MEM:-4096}
VNC=${VNC:-127.0.0.1:2}
OVMF_CODE=${OVMF_CODE:-/usr/share/edk2/ovmf/OVMF_CODE.fd}
OVMF_VARS_SRC=${OVMF_VARS_SRC:-/usr/share/edk2/ovmf/OVMF_VARS.fd}
OVMF_VARS=${OVMF_VARS:-$PWD/build/OVMF_VARS-installer.fd}

[ -f "$ISO" ] || { echo "missing ISO: $ISO" >&2; exit 1; }
[ -f "$OVMF_CODE" ] || { echo "missing $OVMF_CODE: install edk2-ovmf" >&2; exit 1; }
[ -f "$OVMF_VARS_SRC" ] || { echo "missing $OVMF_VARS_SRC: install edk2-ovmf" >&2; exit 1; }

if [ ! -f "$DISK" ]; then
    echo "creating a blank ${DISKSIZE} disk at $DISK"
    truncate -s "$DISKSIZE" "$DISK"
fi
if [ ! -f "$OVMF_VARS" ]; then
    cp "$OVMF_VARS_SRC" "$OVMF_VARS"
fi

rm -f "$MON" "$SERIAL" "$SHOT" "$PWD/build/installer-screen.ppm"

qemu-system-x86_64 \
    -enable-kvm -cpu host -m "$MEM" -smp 4 \
    -drive if=pflash,format=raw,readonly=on,file="$OVMF_CODE" \
    -drive if=pflash,format=raw,file="$OVMF_VARS" \
    -cdrom "$ISO" \
    -drive file="$DISK",format=raw,if=virtio \
    -boot d \
    -vga std \
    -display none -vnc "$VNC" \
    -monitor "unix:$MON,server,nowait" \
    -serial "file:$SERIAL" \
    -no-reboot &
qpid=$!
trap 'kill $qpid 2>/dev/null || true' EXIT


# QEMU monitor helper: talk to the unix socket without socat.
mon() {
    python3 - "$MON" "$1" <<'PY' || true
import socket, sys
s = socket.socket(socket.AF_UNIX)
s.connect(sys.argv[1])
s.sendall((sys.argv[2] + "\n").encode())
s.settimeout(1)
try:
    while s.recv(4096):
        pass
except Exception:
    pass
PY
}

echo "qemu pid $qpid; waiting ${WAIT}s for the installer"
sleep "$WAIT"

if [ -S "$MON" ]; then
    mon "screendump $PWD/build/installer-screen.ppm"
    sleep 2
    if [ -s "$PWD/build/installer-screen.ppm" ]; then
        if command -v convert >/dev/null 2>&1; then
            convert "$PWD/build/installer-screen.ppm" "$SHOT"
            echo "screenshot: $SHOT"
        else
            echo "screenshot: $PWD/build/installer-screen.ppm"
        fi
    fi
    mon quit
fi

wait $qpid 2>/dev/null || true
trap - EXIT

echo "--- serial tail ---"
tail -40 "$SERIAL" || true
