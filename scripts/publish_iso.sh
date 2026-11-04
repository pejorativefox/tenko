#!/usr/bin/env bash
# Publish the installer ISO to the primary site and the LAN mirror.
#
# Writes a fresh <iso>.sha256 next to the image and rsyncs both files to
# tomfool.8bit.ca (public) and to the local-network mirror, so the two
# always carry the same bytes.  Set MIRROR=0 to skip the LAN copy.
#
# Usage:
#   scripts/publish_iso.sh
#   ISO=build/other.iso scripts/publish_iso.sh
set -euo pipefail
cd "$(dirname "$0")/.."

ISO=${ISO:-$PWD/build/browneye-installer.iso}
REMOTE=${REMOTE:-tomfool8@192.200.112.194}
PORT=${PORT:-53211}
PUBLIC=${PUBLIC:-public_html/browneye}
MIRROR=${MIRROR:-daspork@192.168.31.9}
MIRROR_PUBLIC=${MIRROR_PUBLIC:-public_html/browneye}
DRY_RUN=${DRY_RUN:-0}

[ -f "$ISO" ] || { echo "missing ISO: $ISO" >&2; exit 1; }

name=$(basename "$ISO")
sum="$ISO.sha256"
(cd "$(dirname "$ISO")" && sha256sum "$name") > "$sum"
echo "publishing $name ($(du -h "$ISO" | cut -f1))"
cat "$sum"

if [ "$DRY_RUN" = 1 ]; then
    echo "dry run: would upload to $REMOTE:$PUBLIC/iso/ and $MIRROR:$MIRROR_PUBLIC/iso/"
    exit 0
fi

echo "uploading to $REMOTE:$PUBLIC/iso/"
ssh -p "$PORT" "$REMOTE" "mkdir -p $PUBLIC/iso"
rsync -av --partial -e "ssh -p $PORT" "$ISO" "$sum" "$REMOTE:$PUBLIC/iso/"

if [ "$MIRROR" != "0" ]; then
    echo "mirroring to $MIRROR:$MIRROR_PUBLIC/iso/"
    ssh "$MIRROR" "mkdir -p $MIRROR_PUBLIC/iso"
    rsync -av --partial -e "ssh" "$ISO" "$sum" "$MIRROR:$MIRROR_PUBLIC/iso/"
fi

echo
echo "published:"
echo "  https://tomfool.8bit.ca/browneye/iso/$name"
[ "$MIRROR" != "0" ] && echo "  http://192.168.31.9/~daspork/browneye/iso/$name"
