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
TENKO_REPO_URL=${TENKO_REPO_URL:-https://tenko.pjfox.xyz/packages/$TENKO_RELEASE/}
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
