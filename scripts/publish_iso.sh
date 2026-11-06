#!/usr/bin/env bash
# Publish the installer ISO to the primary site and the LAN mirror.
#
# Writes a fresh <iso>.sha256 next to the image and rsyncs both files to
# repo.pjfox.xyz (R2) and to the local-network mirror, so the two
# always carry the same bytes.  Set MIRROR=0 to skip the LAN copy.
#
# Usage:
#   scripts/publish_iso.sh
#   ISO=build/other.iso scripts/publish_iso.sh
set -euo pipefail
cd "$(dirname "$0")/.."

# Keep the unversioned name until the image is rebuilt; a later build can
# publish tenko-installer-6.iso and keep tenko-installer.iso as an alias.
ISO=${ISO:-$PWD/build/tenko-installer.iso}
# Cloudflare R2 (S3) target; the bucket stays r2:browneye during the rename.
R2=${R2:-r2:browneye}
R2_DIR=${R2_DIR:-iso}
MIRROR=${MIRROR:-daspork@192.168.31.9}
MIRROR_PUBLIC=${MIRROR_PUBLIC:-public_html/tenko}
DRY_RUN=${DRY_RUN:-0}

[ -f "$ISO" ] || { echo "missing ISO: $ISO" >&2; exit 1; }

name=$(basename "$ISO")
sum="$ISO.sha256"
(cd "$(dirname "$ISO")" && sha256sum "$name") > "$sum"
echo "publishing $name ($(du -h "$ISO" | cut -f1))"
cat "$sum"

if [ "$DRY_RUN" = 1 ]; then
    echo "dry run: would upload to $R2/$R2_DIR/ and $MIRROR:$MIRROR_PUBLIC/iso/"
    exit 0
fi

echo "uploading to $R2/$R2_DIR/"
rclone copyto "$ISO" "$R2/$R2_DIR/$(basename "$ISO")" --s3-no-check-bucket
rclone copyto "$sum" "$R2/$R2_DIR/$(basename "$sum")" --s3-no-check-bucket

if [ "$MIRROR" != "0" ]; then
    echo "mirroring to $MIRROR:$MIRROR_PUBLIC/iso/"
    ssh "$MIRROR" "mkdir -p $MIRROR_PUBLIC/iso"
    rsync -av --partial -e "ssh" "$ISO" "$sum" "$MIRROR:$MIRROR_PUBLIC/iso/"
fi

echo
echo "published:"
echo "  https://repo.pjfox.xyz/iso/$name"
if [ "$MIRROR" != "0" ]; then
    echo "  http://192.168.31.9/~daspork/tenko/iso/$name"
fi
