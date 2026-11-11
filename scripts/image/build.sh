#!/usr/bin/env bash
# Create or refresh the build image every package is built in.
#
# The image is a root filesystem installed from the offline mirror
# (build/cache/repo): tenko-base, tenko-base-build, tenko-build and the
# extra build packages `tenko image base` installs by default.  `tenko build`
# runs this before every build; it is a no-op while the image is current.
#
# The image is rebuilt when it is missing, or when the mirror changed and has
# newer versions of packages installed in the image (dnf check-update inside
# the image, against the mirror).  Rebuilding is offline and takes a minute
# or two.
#
# Usage:
#   tenko image build            # create/refresh when needed
#   tenko image build --force    # rebuild unconditionally
#
# Environment:
#   BUILD_IMAGE   image tag (default localhost/tenko/build:r6)
#   PACKAGES, DEVEL_PACKAGES   see `tenko image base --help`
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"

repomd=$TENKO_REPO_CACHE/repodata/repomd.xml
[ -f "$repomd" ] || die "no mirror in $TENKO_REPO_CACHE; run tenko sync"
STATE=$TENKO_CACHE_ROOT/cache
STAMP=$STATE/build-image.stamp
mkdir -p "$STATE"

force=0
case "${1:-}" in
    --force) force=1 ;;
    "") ;;
    *) die "usage: tenko image build [--force]" ;;
esac

exec 9>"$STATE/build-image.lock"
flock 9

mirror=$(sha256sum <"$repomd" | cut -d' ' -f1)
image_id() { podman image inspect --format '{{.Id}}' "$BUILD_IMAGE" 2>/dev/null; }

if [ "$force" = 0 ] && old_id=$(image_id); then
    if [ "$(cat "$STAMP" 2>/dev/null)" = "$old_id $mirror" ]; then
        echo "build image is current: $BUILD_IMAGE"
        exit 0
    fi
    rc=0
    podman run --rm --network=none -v "$TENKO_REPO_CACHE:/repo/cache:ro,z" \
        "$BUILD_IMAGE" dnf -q check-update --disablerepo='*' \
        --repofrompath=cache,file:///repo/cache >/dev/null 2>&1 || rc=$?
    if [ "$rc" -eq 0 ]; then
        echo "build image is current with the updated mirror: $BUILD_IMAGE"
        echo "$old_id $mirror" >"$STAMP"
        exit 0
    fi
    if [ "$rc" -eq 100 ]; then
        echo "the mirror has updates for $BUILD_IMAGE; rebuilding"
    else
        echo "warning: could not check $BUILD_IMAGE for updates (dnf exit $rc); rebuilding"
    fi
else
    old_id=$(image_id || true)
    echo "creating $BUILD_IMAGE from $TENKO_REPO_CACHE"
fi

# Use an existing dnf-capable image for the install; lib/rootfs.sh falls
# back to the host's dnf when there is none.
if [ -z "${TOOL_IMAGE:-}" ]; then
    if [ -n "$old_id" ]; then
        TOOL_IMAGE=$BUILD_IMAGE
    else
        TOOL_IMAGE=$BASE_IMAGE
    fi
fi

NO_NEXT_HINT=1 IMAGE=$BUILD_IMAGE TAG_STABLE=0 REPO=$TENKO_REPO_CACHE TOOL_IMAGE=$TOOL_IMAGE \
    ROOTFS=$STATE/build-rootfs TARBALL=$STATE/build-rootfs.tar.gz \
    bash scripts/image/base.sh

# The staging tree and tarball are only inputs to the image.
rm -rf "$STATE/build-rootfs" "$STATE/build-rootfs.tar.gz"
new_id=$(image_id)
echo "$new_id $mirror" >"$STAMP"
if [ -n "$old_id" ] && [ "$old_id" != "$new_id" ]; then
    podman rmi "$old_id" >/dev/null 2>&1 || true
fi
