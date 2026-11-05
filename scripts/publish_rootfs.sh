#!/usr/bin/env bash
# Publish the container rootfs tarball to the primary site and the LAN mirror.
#
# Writes a fresh <tarball>.sha256 next to it and rsyncs both files to
# tomfool.8bit.ca (public) and to the local-network mirror, so the two always
# carry the same bytes.  Set MIRROR=0 to skip the LAN copy.
#
# The tarball is produced by scripts/make_base_image.sh from the published
# RPM set (ROOTFS=build/base-rootfs TARBALL=build/browneye-rootfs.tar.gz).
#
# Usage:
#   scripts/publish_rootfs.sh
#   TARBALL=build/other-rootfs.tar.gz scripts/publish_rootfs.sh
set -euo pipefail
cd "$(dirname "$0")/.."

TARBALL=${TARBALL:-$PWD/build/browneye-rootfs.tar.gz}
REMOTE=${REMOTE:-tomfool8@tomfool.8bit.ca}
PORT=${PORT:-53211}
PUBLIC=${PUBLIC:-public_html/browneye}
MIRROR=${MIRROR:-daspork@192.168.31.9}
MIRROR_PUBLIC=${MIRROR_PUBLIC:-public_html/browneye}
DRY_RUN=${DRY_RUN:-0}

[ -f "$TARBALL" ] || { echo "missing rootfs tarball: $TARBALL" >&2; exit 1; }

name=$(basename "$TARBALL")
sum="$TARBALL.sha256"
(cd "$(dirname "$TARBALL")" && sha256sum "$name") > "$sum"
echo "publishing $name ($(du -h "$TARBALL" | cut -f1))"
cat "$sum"

if [ "$DRY_RUN" = 1 ]; then
    echo "dry run: would upload to $REMOTE:$PUBLIC/rootfs/ and $MIRROR:$MIRROR_PUBLIC/rootfs/"
    exit 0
fi

echo "uploading to $REMOTE:$PUBLIC/rootfs/"
ssh -p "$PORT" "$REMOTE" "mkdir -p $PUBLIC/rootfs"
rsync -av --partial -e "ssh -p $PORT" "$TARBALL" "$sum" "$REMOTE:$PUBLIC/rootfs/"

if [ "$MIRROR" != "0" ]; then
    echo "mirroring to $MIRROR:$MIRROR_PUBLIC/rootfs/"
    ssh "$MIRROR" "mkdir -p $MIRROR_PUBLIC/rootfs"
    rsync -av --partial -e "ssh" "$TARBALL" "$sum" "$MIRROR:$MIRROR_PUBLIC/rootfs/"
fi

echo
echo "published:"
echo "  https://tomfool.8bit.ca/browneye/rootfs/$name"
if [ "$MIRROR" != "0" ]; then
    echo "  http://192.168.31.9/~daspork/browneye/rootfs/$name"
fi
