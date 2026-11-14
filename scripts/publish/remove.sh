#!/usr/bin/env bash
# Remove packages from the published Tenko repository.
#
# Downloads the published repodata, drops every entry for the named packages
# (scripts/publish/remove_packages.py refuses if a remaining package still
# needs one of them), uploads the new metadata, deletes the packages' RPM
# files and regenerates index.html, on R2 and on the LAN mirror.
#
# Usage:
#   tenko publish remove go-bin
#   DRY_RUN=1 tenko publish remove go-bin    # show the plan, change nothing
#
# Requires rclone, modifyrepo_c, zstd, python3, rsync and ssh.  MIRROR=0
# skips the mirror (deliberate local-only tests only).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
. scripts/lib/publish.sh

STAGE=${STAGE:-build/publish-remove}
[ "$#" -gt 0 ] || die "usage: tenko publish remove NAME..."

rm -rf "$STAGE"
mkdir -p "$STAGE"/{old/repodata,xml,filtered}

echo "fetching published repodata from $R2/$REPO_PATH"
rclone copy "$R2/$REPO_PATH/repodata" "$STAGE/old/repodata"
[ -f "$STAGE/old/repodata/repomd.xml" ] ||
    die "no published repodata in $R2/$REPO_PATH"

for mdtype in primary filelists other; do
    zstd -dc "$STAGE"/old/repodata/*-"$mdtype".xml.zst > "$STAGE/xml/$mdtype.xml"
done
python3 scripts/publish/remove_packages.py "$STAGE/xml" "$STAGE/filtered" "$@" \
    > "$STAGE/drop.txt"

# The removed packages' files: the metadata entries plus any older releases
# still lying in the bucket.
rclone lsf "$R2/$REPO_PATH" --files-only | grep '\.rpm$' > "$STAGE/files.txt"
for name in "$@"; do
    grep -E "^${name//./\\.}-[0-9][^-]*-[^-]+\.[a-z0-9_]+\.rpm$" "$STAGE/files.txt" || true
done >> "$STAGE/drop.txt"
sort -u -o "$STAGE/drop.txt" "$STAGE/drop.txt"

cp -a "$STAGE/old/repodata" "$STAGE/repodata"
for mdtype in primary filelists other; do
    modifyrepo_c --mdtype="$mdtype" --compress-type=zstd \
        "$STAGE/filtered/$mdtype.xml" "$STAGE/repodata" >/dev/null 2>&1
done
# modifyrepo_c leaves the replaced files behind; keep only what repomd.xml
# references.
python3 - "$STAGE/repodata" <<'PY'
import os, re, sys
repodata = sys.argv[1]
with open(os.path.join(repodata, "repomd.xml"), encoding="utf-8") as handle:
    keep = {os.path.basename(h) for h in re.findall(r'href="([^"]+)"', handle.read())}
for name in os.listdir(repodata):
    if name != "repomd.xml" and name not in keep:
        os.unlink(os.path.join(repodata, name))
PY

echo "removing:"
sed 's/^/  /' "$STAGE/drop.txt"
if [ "$DRY_RUN" = 1 ]; then
    echo "dry run: staged in $STAGE; nothing changed"
    exit 0
fi

echo "uploading metadata"
rclone sync "$STAGE/repodata" "$R2/$REPO_PATH/repodata" --s3-no-check-bucket
echo "deleting RPMs"
rclone delete "$R2/$REPO_PATH" --files-from "$STAGE/drop.txt"

echo "regenerating index.html"
rclone lsf "$R2/$REPO_PATH" --files-only --format "ps" --separator " " |
    grep '\.rpm ' > "$STAGE/index-files.txt"
python3 scripts/publish/repo_index.py "$STAGE/index-files.txt" "$STAGE/index.html" \
    "$TENKO_RELEASE" "$URL" "$REPO_ID"
rclone copyto "$STAGE/index.html" "$R2/$REPO_PATH/index.html" --s3-no-check-bucket

if mirror_enabled; then
    echo "updating $MIRROR:$MIRROR_PUBLIC/$REPO_PATH/"
    rsync -a --delete -e ssh "$STAGE/repodata/" \
        "$MIRROR:$MIRROR_PUBLIC/$REPO_PATH/repodata/"
    ssh "$MIRROR" "cd $MIRROR_PUBLIC/$REPO_PATH && xargs rm -f" < "$STAGE/drop.txt"
    rsync -a -e ssh "$STAGE/index.html" "$MIRROR:$MIRROR_PUBLIC/$REPO_PATH/index.html"
fi

echo "removed: $*"
echo "verify: dnf --refresh --disablerepo='*' --repofrompath=t,$URL repoquery $*"
