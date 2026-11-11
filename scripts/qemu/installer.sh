#!/usr/bin/env bash
# Boot the installer ISO in QEMU (UEFI/OVMF) and capture the screen.
#
# The disk is blank: the installer should offer it in the disk list and let
# you create a GPT.  Serial output goes to build/installer-serial.log, the
# screenshot to build/installer-screen.png.
#
# Usage:
#   tenko qemu installer
#   ISO=build/other.iso WAIT=120 tenko qemu installer
#
# Environment: ISO, DISK, DISKSIZE (20G), WAIT (90), MEM (4096), VNC
# (127.0.0.1:2), OVMF_CODE, OVMF_VARS_SRC, OVMF_VARS, SERIAL, MON, SHOT.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
MEM=${MEM:-4096}
VNC=${VNC:-127.0.0.1:2}
. scripts/lib/qemu.sh

ISO=${ISO:-$PWD/build/tenko-installer.iso}
DISK=${DISK:-$PWD/build/installer-test.img}
DISKSIZE=${DISKSIZE:-20G}
SERIAL=${SERIAL:-$PWD/build/installer-serial.log}
MON=${MON:-$PWD/build/installer-monitor.sock}
SHOT=${SHOT:-$PWD/build/installer-screen.png}
WAIT=${WAIT:-90}
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

rm -f "$MON" "$SERIAL" "$SHOT"

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


echo "qemu pid $qpid; waiting ${WAIT}s for the installer"
sleep "$WAIT"

screendump "$SHOT" || echo "no screendump" >&2
mon quit

wait $qpid 2>/dev/null || true
trap - EXIT

echo "--- serial tail ---"
tail -40 "$SERIAL" || true
