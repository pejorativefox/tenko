#!/usr/bin/env bash
# Publish one or more already-built RPMs to the Browneye repository without
# mirroring the whole repository first.
#
# The published repodata is the source of truth: this script downloads only
# repodata/ (a few hundred KiB), merges the new RPMs into it with
# mergerepo_c --method nvr (so a newer release replaces the entry for the same
# package instead of being ignored), uploads the RPMs plus the merged
# metadata, and regenerates index.html from the server's own file listing.
#
# Merging keeps every package already in the repository, so a single-package
# update cannot drop the rest of the tree the way a fresh createrepo_c over a
# partial local tree would.
#
# Usage:
#   scripts/publish_rpm.sh ~/rpmbuild/RPMS/x86_64/htop-3.5.3-1.x86_64.rpm
#   PRUNE=1 scripts/publish_rpm.sh podman-bin-6.1.4-2.x86_64.rpm
#       also delete RPM files the merged metadata no longer references
#       (superseded releases); off by default.
#   DRY_RUN=1 scripts/publish_rpm.sh foo.rpm
#       stage and merge locally, print the plan, upload nothing.
#
# Requires createrepo_c, mergerepo_c, rsync, ssh, zstd and python3 on the host.
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION=${VERSION:-13.1}
REMOTE=${REMOTE:-tomfool8@192.200.112.194}
PORT=${PORT:-53211}
PUBLIC=${PUBLIC:-public_html/browneye}
DEST=${DEST:-$PUBLIC/packages/$VERSION/}
URL=${URL:-https://tomfool.8bit.ca/browneye/packages/$VERSION/}
REPO_ID=browneye-$VERSION
STAGE=${STAGE:-build/publish-rpm}
PRUNE=${PRUNE:-0}
DRY_RUN=${DRY_RUN:-0}
SSH_CMD=(ssh -p "$PORT")

[ "$#" -gt 0 ] || { echo "usage: $0 RPM..." >&2; exit 2; }

rpms=()
for arg in "$@"; do
    [ -f "$arg" ] || { echo "missing RPM: $arg" >&2; exit 1; }
    rpm -qp --qf '' "$arg" >/dev/null 2>&1 || {
        echo "not a readable RPM: $arg" >&2; exit 1; }
    rpms+=("$arg")
done

rm -rf "$STAGE"
mkdir -p "$STAGE"/{new,merged}
mkdir -p "$STAGE/old/repodata"

echo "fetching published repodata from $REMOTE"
rsync -a -e "ssh -p $PORT" "$REMOTE:$DEST/repodata/" "$STAGE/old/repodata/"

for rpm in "${rpms[@]}"; do
    cp -p "$rpm" "$STAGE/new/"
done
createrepo_c --quiet "$STAGE/new"

# nvr keeps the highest version-release per package name/arch across the two
# repositories, so publishing foo-2 over an existing foo-1 replaces the index
# entry instead of keeping whichever repo was merged first.
#
# --omit-baseurl is mandatory: mergerepo_c otherwise stamps every package with
# xml:base pointing at the local staging directories ("repo-old", "repo-new"),
# and dnf then tries to download from http://repo-old/<rpm>.
mergerepo_c --method nvr --omit-baseurl \
    --repo "$STAGE/old" --repo "$STAGE/new" \
    -o "$STAGE/merged" >/dev/null

# The published metadata can already be poisoned: an earlier merge without
# --omit-baseurl stamped every package with xml:base="repo-old", and merging
# preserves that attribute, so dnf keeps looking for http://repo-old/<rpm>.
# Strip any xml:base from the merged metadata and let modifyrepo_c rewrite
# repomd.xml with the new checksums.  (grep -q would SIGPIPE zstd and make the
# pipeline look empty under pipefail, hence the temp files.)
mkdir -p "$STAGE/strip"
for mdtype in primary filelists other updateinfo; do
    if ! ls "$STAGE/merged"/repodata/*-"$mdtype".xml.zst >/dev/null 2>&1; then
        continue
    fi
    zstd -dc "$STAGE/merged"/repodata/*-"$mdtype".xml.zst \
        > "$STAGE/strip/$mdtype.xml"
    sed -i 's/ xml:base="[^"]*"//g' "$STAGE/strip/$mdtype.xml"
    modifyrepo_c --mdtype="$mdtype" --compress-type=zstd \
        "$STAGE/strip/$mdtype.xml" "$STAGE/merged/repodata" >/dev/null 2>&1
done

# modifyrepo_c keeps the old, now unreferenced metadata files next to the new
# ones; upload only what repomd.xml points at.
python3 - "$STAGE/merged/repodata" <<'PY'
import os
import re
import sys

repodata = sys.argv[1]
with open(os.path.join(repodata, "repomd.xml"), encoding="utf-8") as handle:
    keep = {os.path.basename(href) for href in
            re.findall(r'href="([^"]+)"', handle.read())}
for name in os.listdir(repodata):
    if name != "repomd.xml" and name not in keep:
        os.unlink(os.path.join(repodata, name))
PY

if grep -q 'xml:base=' "$STAGE"/strip/*.xml; then
    echo "refusing to publish: merged metadata still contains xml:base entries" >&2
    grep -ho 'xml:base="[^"]*"' "$STAGE"/strip/*.xml | sort -u >&2
    exit 1
fi

count_of() { zstd -dc "$1"/repodata/*primary.xml.zst | grep -c '<package type='; }
old_count=$(count_of "$STAGE/old")
merged_count=$(count_of "$STAGE/merged")
new_count=$(count_of "$STAGE/new")
echo "packages: published $old_count, new $new_count, merged $merged_count"
if [ "$merged_count" -lt "$old_count" ]; then
    echo "refusing to publish: merged metadata has fewer packages than the" \
         "published set ($merged_count < $old_count)" >&2
    exit 1
fi

# The package must be in the merged metadata at the exact version-release we
# just built; a plain name match would still pass if the merge had kept an
# older release, which is the failure this merge method exists to prevent.
for rpm in "${rpms[@]}"; do
    read -r name ver rel <<<"$(rpm -qp --qf '%{NAME} %{VERSION} %{RELEASE}\n' "$rpm")"
    if zstd -dc "$STAGE/merged"/repodata/*primary.xml.zst |
            grep -A4 "<name>${name}</name>" |
            grep -q "ver=\"${ver}\" rel=\"${rel}\""; then
        echo "  merged metadata has ${name}-${ver}-${rel}"
    else
        echo "error: ${name}-${ver}-${rel} missing from merged metadata" >&2
        exit 1
    fi
done

if [ "$DRY_RUN" = 1 ]; then
    echo "dry run: staged in $STAGE; nothing uploaded"
    exit 0
fi

echo "uploading RPMs"
rsync -av -e "ssh -p $PORT" "${rpms[@]}" "$REMOTE:$DEST"

echo "uploading merged metadata"
rsync -av --delete -e "ssh -p $PORT" "$STAGE/merged/repodata/" \
    "$REMOTE:$DEST/repodata/"

if [ "$PRUNE" = 1 ]; then
    echo "pruning RPMs the merged metadata does not reference"
    zstd -dc "$STAGE/merged"/repodata/*primary.xml.zst |
        grep -o 'href="[^"]*\.rpm"' | cut -d'"' -f2 | sort -u > "$STAGE/keep.txt"
    "${SSH_CMD[@]}" "$REMOTE" "cd ~/$DEST && ls *.rpm" |
        while read -r name; do
            grep -qxF "$name" "$STAGE/keep.txt" || echo "$name"
        done > "$STAGE/drop.txt"
    if [ -s "$STAGE/drop.txt" ]; then
        sed 's/^/  drop /' "$STAGE/drop.txt"
        "${SSH_CMD[@]}" "$REMOTE" \
            "cd ~/$DEST && xargs rm -f" < "$STAGE/drop.txt"
    else
        echo "  nothing to prune"
    fi
fi

echo "regenerating index.html"
"${SSH_CMD[@]}" "$REMOTE" \
    "cd ~/$DEST && find . -maxdepth 1 -name '*.rpm' -printf '%f %s\n'" \
    > "$STAGE/files.txt"
python3 scripts/gen_repo_index.py "$STAGE/files.txt" "$STAGE/index.html" \
    "$VERSION" "$URL" "$REPO_ID"
rsync -av -e "ssh -p $PORT" "$STAGE/index.html" "$REMOTE:$DEST/index.html"

echo
echo "published:"
for rpm in "${rpms[@]}"; do
    echo "  $(basename "$rpm")"
done
echo "verify: dnf --refresh -y --disablerepo='*' --repofrompath=t,$URL list --available <package>"
echo "repo:   $URL"
