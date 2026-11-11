#!/usr/bin/env bash
# Publish the installer ISO or the rootfs tarball to the public site and
# the LAN mirror.
#
# Writes a fresh <file>.sha256 next to the file and uploads both, so the two
# targets always carry the same bytes.
#
# Usage:
#   tenko publish iso [FILE]       # default build/tenko-installer.iso -> iso/
#   tenko publish rootfs [FILE]    # default build/tenko-rootfs.tar.gz -> rootfs/
#
# `tenko image iso` and `tenko image base` produce the default files.  Only
# rebuild and publish images when asked to (see AGENTS.md).
#
# Environment: DRY_RUN=1 uploads nothing; MIRROR=0 skips the LAN mirror
# (local-only tests); R2, MIRROR, MIRROR_PUBLIC override the targets.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
. scripts/lib/publish.sh

# Keep the unversioned names until the images are rebuilt; a later build can
# publish tenko-installer-6.iso / tenko-rootfs-6.tar.gz with an alias.
kind=${1:-}
case "$kind" in
    iso) file=${2:-build/tenko-installer.iso} ;;
    rootfs) file=${2:-build/tenko-rootfs.tar.gz} ;;
    *) die "usage: tenko publish {iso|rootfs} [FILE]" ;;
esac
[ -f "$file" ] || die "missing $kind file: $file"

name=$(basename "$file")
sum="$file.sha256"
(cd "$(dirname "$file")" && sha256sum "$name") >"$sum"
echo "publishing $name ($(du -h "$file" | cut -f1))"
cat "$sum"

publish_files "$kind" "$file" "$sum"

[ "$DRY_RUN" = 1 ] && exit 0
echo
echo "published:"
echo "  $PUBLIC_URL/$kind/$name"
if mirror_enabled; then
    echo "  $MIRROR_URL/$kind/$name"
fi
