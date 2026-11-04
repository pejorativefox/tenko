#!/usr/bin/env bash
# Assemble the single Browneye repository: the base repo, every RPM produced
# by the BLFS/XFCE/desktop build runs, and every RPM staged by the package
# split waves.  There is no separate desktop repository.
#
# The repo is the union of:
#   - $BASE        base repo produced by the container base rebuild
#                  (default build/repo-selfhost)
#   - build/blfs-parity-*/build/*/RPMS/*/    desktop/XFCE/kernel builds
#   - $STAGING     wave builds done in separate git worktrees
#                  (default build/rpm-staging)
#   - $EXTRA_RPM_DIRS  colon-separated one-off directories
#
# Anything built in a worktree must be copied into $STAGING first (or passed
# via EXTRA_RPM_DIRS), otherwise it is silently dropped from the repo.
#
# Usage: scripts/assemble_repo.sh [REPO]
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/repo_tools.sh

REPO=${REPO:-build/repo-all}
BASE=${BASE:-build/repo-selfhost}
STAGING=${STAGING:-build/rpm-staging}
EXTRA_RPM_DIRS=${EXTRA_RPM_DIRS:-}

[ -d "$BASE" ] || { echo "missing base repo: $BASE" >&2; exit 1; }

copy_from() {
    local src=$1
    [ -d "$src" ] || return 0
    cp -pf "$src"/*.rpm "$REPO"/ 2>/dev/null || true
}

rm -rf "$REPO"
mkdir -p "$REPO"

copy_from "$BASE"

# Later build runs overwrite earlier ones; every phase directory is included.
for dir in build/blfs-parity-*/build/*/RPMS/*/; do
    copy_from "${dir%/}"
done

# RPMs built in the per-wave worktrees (firmware, Python, runtime/toolchain/
# base splits, make-ca, ...).  The base repo is only as fresh as its last
# container rebuild, so this is what keeps the split packages in the tree.
copy_from "$STAGING"

# One-off extras, e.g. EXTRA_RPM_DIRS=$HOME/rpmbuild/RPMS/x86_64
if [ -n "$EXTRA_RPM_DIRS" ]; then
    IFS=: read -r -a extra_dirs <<<"$EXTRA_RPM_DIRS"
    for dir in "${extra_dirs[@]}"; do
        copy_from "$dir"
    done
fi

# The kernel is built in the container (E2) and is collected above with
# every other blfs-parity RPM; no host copy is needed.

./scripts/prune_repo.sh "$REPO"

count=$(find "$REPO" -maxdepth 1 -name '*.rpm' | wc -l)
echo "repo RPMs: $count"
createrepo "$REPO"
echo "wrote $REPO"