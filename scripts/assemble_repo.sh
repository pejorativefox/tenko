#!/usr/bin/env bash
# Assemble the single Browneye repository: the base repo plus every RPM
# produced by the BLFS/XFCE/desktop build runs.  There is no separate
# desktop repository.
#
# Usage: scripts/assemble_repo.sh [REPO]
set -euo pipefail
cd "$(dirname "$0")/.."

REPO=${REPO:-build/repo-all}
BASE=${BASE:-build/repo-selfhost}

[ -d "$BASE" ] || { echo "missing base repo: $BASE" >&2; exit 1; }

rm -rf "$REPO"
mkdir -p "$REPO"
cp -p "$BASE"/*.rpm "$REPO"/ 2>/dev/null || true

# Later build runs overwrite earlier ones; every phase directory is included.
for dir in build/blfs-parity-*/build/*/RPMS/*/; do
    cp -pf "$dir"*.rpm "$REPO"/ 2>/dev/null || true
done

# The kernel is built in the container (E2) and is collected above with
# every other blfs-parity RPM; no host copy is needed.

count=$(find "$REPO" -maxdepth 1 -name '*.rpm' | wc -l)
echo "repo RPMs: $count"
createrepo_c --quiet "$REPO"
echo "wrote $REPO"
