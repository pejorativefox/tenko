#!/usr/bin/env bash
# Run the installer UI against synthetic disks with the real planner and a
# dry-run command runner.  No root, UEFI firmware, live medium or network is
# needed, so the curses flow can be iterated on without rebuilding the ISO.
#
# Usage:
#   tenko installer-sim
#   tenko installer-sim --simulate-scenario mixed
#   TENKO_SIM_DIR=/tmp/my-sim tenko installer-sim
#
# The planned commands are written to plan.sh under the simulation directory
# (default /tmp/tenko-installer-sim).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"

if [ ! -t 0 ] || [ ! -t 1 ]; then
    echo "note: no TTY; the installer will use its line-oriented mode" >&2
fi

exec python3 package_specs/tenko-installer/files/main.py --simulate "$@"
