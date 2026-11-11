#!/usr/bin/env bash
# Boot the base system (the installer's "base" package set) in QEMU and wait
# for a login prompt on the serial console.
#
# Usage:
#   tenko qemu boot
#   REPO=https://tenko.pjfox.xyz/packages/6/ tenko qemu boot
#
# The root filesystem is installed from the offline mirror (see
# scripts/lib/qemu.sh) and reused while the repository is unchanged.  The
# serial log is build/qemu-boot.log.  Exit status: 0 login prompt reached,
# 1 boot failed or timed out.
#
# Environment: WAIT (seconds, default 180), EXTRA_PACKAGES, REBUILD_ROOTFS=1,
# plus the settings in scripts/lib/qemu.sh.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
. scripts/lib/qemu.sh

ROOTFS=${ROOTFS:-$PWD/build/rootfs-boot}
IMG=${IMG:-$PWD/build/boot.img}
SERIAL=${SERIAL:-$PWD/build/qemu-boot.log}
MON=${MON:-$PWD/build/qemu-boot.sock}
WAIT=${WAIT:-180}

# shellcheck disable=SC2086
test_rootfs "$ROOTFS" base ${EXTRA_PACKAGES:-}
disk_image "$ROOTFS" "$IMG" 4G

qemu_start "$ROOTFS" "$IMG"
echo "booting (up to ${WAIT}s); serial log: $SERIAL"
if qemu_wait_serial ' login: ' "$WAIT"; then
    result=0
    echo "login prompt reached"
else
    result=1
    echo "no login prompt after ${WAIT}s" >&2
    tail -40 "$SERIAL" >&2 || true
fi
failed=$(grep -a 'FAILED' "$SERIAL" | sed 's/\x1b\[[0-9;]*m//g' | sort -u || true)
if [ -n "$failed" ]; then
    echo "units that failed during boot:"
    printf '  %s\n' "$failed"
fi
qemu_stop
exit "$result"
