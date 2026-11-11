#!/usr/bin/env bash
# Create or refresh an image packages are built in.
#
# Both images are root filesystems installed from the offline mirror
# (build/cache/repo):
#   full     BUILD_IMAGE (localhost/tenko/build:r6): tenko-base (which
#            carries tenko-base-build and tenko-buildroot) and the extra
#            build packages `tenko image base` installs by default.
#            STRICT=0 builds.
#   --strict BUILDROOT_IMAGE (localhost/tenko/buildroot:r6): only
#            tenko-buildroot, the toolchain baseline, so a build sees
#            nothing its spec does not declare.  STRICT=1 builds.
# `tenko build` runs this before every build; it is a no-op while the image
# is current.
#
# The image is rebuilt when it is missing, or when the mirror changed and has
# newer versions of packages installed in the image (dnf check-update inside
# the image, against the mirror).  Rebuilding is offline and takes a minute
# or two.
#
# Usage:
#   tenko image build [--strict]           # create/refresh when needed
#   tenko image build [--strict] --force   # rebuild unconditionally
#
# Environment:
#   BUILD_IMAGE, BUILDROOT_IMAGE   image tags
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"

repomd=$TENKO_REPO_CACHE/repodata/repomd.xml
[ -f "$repomd" ] || die "no mirror in $TENKO_REPO_CACHE; run tenko sync"
STATE=$TENKO_CACHE_ROOT/cache
mkdir -p "$STATE"

force=0 flavor=build
for arg in "$@"; do
    case "$arg" in
        --force) force=1 ;;
        --strict) flavor=buildroot ;;
        *) die "usage: tenko image build [--strict] [--force]" ;;
    esac
done
if [ "$flavor" = buildroot ]; then
    IMAGE_TAG=$BUILDROOT_IMAGE
    PACKAGES=tenko-buildroot
    VERIFY_RPM=tenko-buildroot
else
    IMAGE_TAG=$BUILD_IMAGE
    PACKAGES=${PACKAGES:-}
    VERIFY_RPM=tenko-base
fi
STAMP=$STATE/$flavor-image.stamp

exec 9>"$STATE/$flavor-image.lock"
flock 9

mirror=$(sha256sum <"$repomd" | cut -d' ' -f1)
image_id() { podman image inspect --format '{{.Id}}' "$IMAGE_TAG" 2>/dev/null; }

if [ "$force" = 0 ] && old_id=$(image_id); then
    if [ "$(cat "$STAMP" 2>/dev/null)" = "$old_id $mirror" ]; then
        echo "build image is current: $IMAGE_TAG"
        exit 0
    fi
    rc=0
    podman run --rm --network=none -v "$TENKO_REPO_CACHE:/repo/cache:ro,z" \
        "$IMAGE_TAG" dnf -q check-update --disablerepo='*' \
        --repofrompath=cache,file:///repo/cache >/dev/null 2>&1 || rc=$?
    if [ "$rc" -eq 0 ]; then
        echo "build image is current with the updated mirror: $IMAGE_TAG"
        echo "$old_id $mirror" >"$STAMP"
        exit 0
    fi
    if [ "$rc" -eq 100 ]; then
        echo "the mirror has updates for $IMAGE_TAG; rebuilding"
    else
        echo "warning: could not check $IMAGE_TAG for updates (dnf exit $rc); rebuilding"
    fi
else
    old_id=$(image_id || true)
    echo "creating $IMAGE_TAG from $TENKO_REPO_CACHE"
fi

# Use an existing dnf-capable image for the install; lib/rootfs.sh falls
# back to the host's dnf when there is none.
if [ -z "${TOOL_IMAGE:-}" ]; then
    if [ -n "$old_id" ]; then
        TOOL_IMAGE=$IMAGE_TAG
    elif podman image exists "$BUILD_IMAGE"; then
        TOOL_IMAGE=$BUILD_IMAGE
    else
        TOOL_IMAGE=$BASE_IMAGE
    fi
fi

NO_NEXT_HINT=1 IMAGE=$IMAGE_TAG TAG_STABLE=0 REPO=$TENKO_REPO_CACHE TOOL_IMAGE=$TOOL_IMAGE \
    ROOTFS=$STATE/$flavor-rootfs TARBALL=$STATE/$flavor-rootfs.tar.gz \
    PACKAGES=$PACKAGES VERIFY_RPM=$VERIFY_RPM bash scripts/image/base.sh

# The staging tree and tarball are only inputs to the image.
rm -rf "$STATE/$flavor-rootfs" "$STATE/$flavor-rootfs.tar.gz"
new_id=$(image_id)
echo "$new_id $mirror" >"$STAMP"
if [ -n "$old_id" ] && [ "$old_id" != "$new_id" ]; then
    podman rmi "$old_id" >/dev/null 2>&1 || true
fi
