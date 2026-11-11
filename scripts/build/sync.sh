#!/usr/bin/env bash
# Mirror the published repository into build/cache/repo for offline builds.
#
# Each RPM is downloaded once; later syncs fetch only repomd.xml when nothing
# changed, and only new packages when something did.  `tenko build` runs this
# automatically (set OFFLINE=1 to skip it).
#
# Usage:
#   tenko sync
#
# Environment:
#   SYNC_URLS          repositories to try in order (default: the LAN mirror,
#                      then the public site)
#   TENKO_REPO_CACHE   mirror directory (default build/cache/repo)
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"

SYNC_URLS=${SYNC_URLS:-"$MIRROR_URL/packages/$TENKO_RELEASE/ $TENKO_REPO_URL"}
export SYNC_URLS
exec python3 scripts/build/sync_repo.py --dest "$TENKO_REPO_CACHE"
