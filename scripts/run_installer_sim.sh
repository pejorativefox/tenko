#!/usr/bin/env bash
# Run the installer UI against synthetic disks with the real planner and a
# dry-run command runner.  No root, UEFI firmware, live medium or network is
# needed, so the curses flow can be iterated on without rebuilding the ISO.
#
# Usage:
#   scripts/run_installer_sim.sh
#   scripts/run_installer_sim.sh --simulate-scenario mixed
#   BROWNEYE_SIM_DIR=/tmp/my-sim scripts/run_installer_sim.sh
#
# The planned commands are written to plan.sh under the simulation directory
# (default /tmp/browneye-installer-sim).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -t 0 ] || [ ! -t 1 ]; then
    echo "note: no TTY; the installer will use its line-oriented mode" >&2
fi

exec python3 package_specs/browneye-installer/files/main.py --simulate "$@"
