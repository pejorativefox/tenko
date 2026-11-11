# Shared setup for the scripts behind ./tenko.  Source it first:
#
#   . "$(dirname "$0")/../lib/common.sh"
#
# It changes to the repository root and defines the defaults every command
# shares.  Each one can be overridden from the environment.

TENKO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$TENKO_ROOT"

# Distro release and the published repository.
TENKO_RELEASE=${TENKO_RELEASE:-6}
PUBLIC_URL=${PUBLIC_URL:-https://tenko.pjfox.xyz}
TENKO_REPO_URL=${TENKO_REPO_URL:-$PUBLIC_URL/packages/$TENKO_RELEASE/}
# LAN mirror of the public site (same bytes; see AGENTS.md).
MIRROR_URL=${MIRROR_URL:-http://192.168.31.9/~daspork/tenko}
# Container image used for rpmbuild, ISO authoring and the dnf helpers.
# `tenko image base` creates it.
BASE_IMAGE=${BASE_IMAGE:-localhost/tenko/base:r$TENKO_RELEASE}
# Kernel version installed into rootfs and ISO images.
KVER=${KVER:-7.3.1}

die() {
    echo "$*" >&2
    exit 1
}

# repo_url PATH-OR-URL: a baseurl dnf accepts (local directories become
# absolute file:// URLs).
repo_url() {
    case "$1" in
        http://*|https://*|ftp://*|file://*) printf '%s\n' "$1" ;;
        *) [ -d "$1" ] || die "missing repository: $1"
           printf 'file://%s\n' "$(cd "$1" && pwd)" ;;
    esac
}

# abspath PATH: absolute path for PATH, whose parent must exist.
abspath() {
    printf '%s/%s\n' "$(cd "$(dirname "$1")" && pwd)" "$(basename "$1")"
}

# Local build state (see docs/build.md).  The download caches are checksum-
# verified, so every worktree shares the main checkout's copies:
#   <main>/build/cache/repo  offline mirror of the published repo (tenko sync)
#   <main>/build/sources     md5-verified source tarballs
# Locally built RPMs stay per checkout, so a branch cannot leak into another:
#   build/repo               RPMs built here, preferred over the mirror
_main=$(git -C "$TENKO_ROOT" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
TENKO_CACHE_ROOT=${TENKO_CACHE_ROOT:-${_main:+$(dirname "$_main")/build}}
TENKO_CACHE_ROOT=${TENKO_CACHE_ROOT:-$TENKO_ROOT/build}
TENKO_REPO_CACHE=${TENKO_REPO_CACHE:-$TENKO_CACHE_ROOT/cache/repo}
TENKO_SOURCES_DIR=${TENKO_SOURCES_DIR:-$TENKO_CACHE_ROOT/sources}
TENKO_LOCAL_REPO=${TENKO_LOCAL_REPO:-$TENKO_ROOT/build/repo}
# Image every package is built in; created and refreshed by `tenko build`.
BUILD_IMAGE=${BUILD_IMAGE:-localhost/tenko/build:r$TENKO_RELEASE}
export TENKO_REPO_CACHE TENKO_LOCAL_REPO TENKO_SOURCES_DIR
