#!/usr/bin/env bash
# Publish the container rootfs tarball to the primary site and the LAN mirror.
#
# Writes a fresh <tarball>.sha256 next to it and rsyncs both files to
# repo.pjfox.xyz (R2) and to the local-network mirror, so the two always
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
# Cloudflare R2 (S3) target for the public tree; the LAN mirror stays on rsync.
R2=${R2:-r2:browneye}
R2_DIR=${R2_DIR:-rootfs}
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
    echo "dry run: would upload to $R2/$R2_DIR/ and $MIRROR:$MIRROR_PUBLIC/rootfs/"
    exit 0
fi

echo "uploading to $R2/$R2_DIR/"
rclone copyto "$TARBALL" "$R2/$R2_DIR/$(basename "$TARBALL")"
rclone copyto "$sum" "$R2/$R2_DIR/$(basename "$sum")"

if [ "$MIRROR" != "0" ]; then
    echo "mirroring to $MIRROR:$MIRROR_PUBLIC/rootfs/"
    ssh "$MIRROR" "mkdir -p $MIRROR_PUBLIC/rootfs"
    rsync -av --partial -e "ssh" "$TARBALL" "$sum" "$MIRROR:$MIRROR_PUBLIC/rootfs/"
fi

echo
echo "published:"
echo "  https://repo.pjfox.xyz/rootfs/$name"
if [ "$MIRROR" != "0" ]; then
    echo "  http://192.168.31.9/~daspork/browneye/rootfs/$name"
fi
