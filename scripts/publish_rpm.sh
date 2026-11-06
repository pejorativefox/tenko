#!/usr/bin/env bash
# Publish one or more already-built RPMs to the Tenko repository without
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
# Requires createrepo_c, mergerepo_c, rclone, zstd and python3 on the host;
# the LAN mirror step additionally needs rsync and ssh.
set -euo pipefail
cd "$(dirname "$0")/.."

TENKO_RELEASE=${TENKO_RELEASE:-6}
# Cloudflare R2 (S3) target; the bucket stays r2:browneye during the rename.
# Keep packages/13.1 in the bucket as the external compatibility alias.
R2=${R2:-r2:browneye}
R2_PATH=${R2_PATH:-tenko/packages/$TENKO_RELEASE}
# LAN mirror (also refreshed by publish_repo.sh); set MIRROR=0 to skip.
# The old public_html/browneye symlink remains the external alias.
MIRROR=${MIRROR:-daspork@192.168.31.9}
MIRROR_PUBLIC=${MIRROR_PUBLIC:-public_html/tenko}
URL=${URL:-https://repo.pjfox.xyz/tenko/packages/$TENKO_RELEASE/}
REPO_ID=tenko-$TENKO_RELEASE
STAGE=${STAGE:-build/publish-rpm}
PRUNE=${PRUNE:-0}
DRY_RUN=${DRY_RUN:-0}

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

echo "fetching published repodata from $R2/$R2_PATH"
rclone copy "$R2/$R2_PATH/repodata" "$STAGE/old/repodata"
[ -f "$STAGE/old/repodata/repomd.xml" ] || {
    echo "error: no published repodata in $R2/$R2_PATH" >&2; exit 1; }

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

# The published repository is sometimes regenerated from the full file
# listing (publish_repo.sh), so its metadata can list superseded NEVRAs that
# mergerepo_c --method nvr intentionally collapses to the highest release.
# Compare the distinct (name, arch) sets instead of raw entry counts: a merge
# must never lose a package, but a smaller entry count is expected.
python3 - "$STAGE" <<'PY'
import glob
import io
import subprocess
import sys
import xml.etree.ElementTree as ET

stage = sys.argv[1]
ns = {"c": "http://linux.duke.edu/metadata/common"}

def packages(path):
    data = subprocess.check_output(["zstd", "-dc", path])
    keys = set()
    for _, el in ET.iterparse(io.BytesIO(data)):
        if el.tag.endswith("}package"):
            keys.add((el.find("c:name", ns).text,
                      el.find("c:arch", ns).text))
            el.clear()
    return keys

old = packages(glob.glob(stage + "/old/repodata/*primary.xml.zst")[0])
new = packages(glob.glob(stage + "/new/repodata/*primary.xml.zst")[0])
merged = packages(glob.glob(stage + "/merged/repodata/*primary.xml.zst")[0])
missing = old - merged
if missing:
    print("refusing to publish: merged metadata dropped %d package(s): %s"
          % (len(missing),
             ", ".join("%s.%s" % key for key in sorted(missing)[:5])),
          file=sys.stderr)
    sys.exit(1)
print("packages: published %d, new %d, merged %d (distinct name/arch)"
      % (len(old), len(new), len(merged)))
PY

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

# A repeated NEVRA with different content is a metadata hazard: mergerepo_c
# --method nvr keeps the published entry while rsync overwrites the file, so
# dnf then sees a size/checksum mismatch.  Refuse it; bump Release instead.
python3 - "$STAGE" "${rpms[@]}" <<'PY'
import glob
import hashlib
import io
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

stage = sys.argv[1]
rpms = sys.argv[2:]
ns = {"c": "http://linux.duke.edu/metadata/common"}
data = subprocess.check_output(
    ["zstd", "-dc", glob.glob(os.path.join(stage, "old/repodata/*primary.xml.zst"))[0]])
published = {}
for _, el in ET.iterparse(io.BytesIO(data)):
    if el.tag.endswith("}package"):
        ver = el.find("c:version", ns)
        key = (el.find("c:name", ns).text, ver.get("ver"), ver.get("rel"),
               el.find("c:arch", ns).text)
        size = el.find("c:size", ns)
        csum = el.find("c:checksum", ns)
        published[key] = (int(size.get("package")) if size is not None else None,
                          csum.text if csum is not None else None)
        el.clear()

bad = []
for path in rpms:
    query = "%{NAME}\t%{VERSION}\t%{RELEASE}\t%{ARCH}"
    name, ver, rel, arch = subprocess.check_output(
        ["rpm", "-qp", "--qf", query, path], text=True).strip().split("\t")
    key = (name, ver, rel, arch)
    if key not in published:
        continue
    size = os.path.getsize(path)
    with open(path, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    old_size, old_digest = published[key]
    if (old_size is not None and old_size != size) or (
            old_digest is not None and old_digest != digest):
        bad.append(key)
if bad:
    for name, ver, rel, arch in bad:
        print("error: {}-{}-{}.{} already exists with different content; "
              "bump Release before publishing".format(name, ver, rel, arch),
              file=sys.stderr)
    sys.exit(1)
PY

if [ "$DRY_RUN" = 1 ]; then
    echo "dry run: staged in $STAGE; nothing uploaded"
    exit 0
fi

echo "uploading RPMs"
for rpm in "${rpms[@]}"; do
    rclone copy "$rpm" "$R2/$R2_PATH/" --s3-no-check-bucket
done

echo "uploading merged metadata"
rclone sync "$STAGE/merged/repodata" "$R2/$R2_PATH/repodata" --s3-no-check-bucket

if [ "$PRUNE" = 1 ]; then
    echo "pruning RPMs the merged metadata does not reference"
    zstd -dc "$STAGE/merged"/repodata/*primary.xml.zst |
        grep -o 'href="[^"]*\.rpm"' | cut -d'"' -f2 | sort -u > "$STAGE/keep.txt"
    rclone lsf "$R2/$R2_PATH" --files-only | grep '\.rpm$' |
        while read -r name; do
            grep -qxF "$name" "$STAGE/keep.txt" || echo "$name"
        done > "$STAGE/drop.txt"
    if [ -s "$STAGE/drop.txt" ]; then
        sed 's/^/  drop /' "$STAGE/drop.txt"
        rclone delete "$R2/$R2_PATH" --files-from "$STAGE/drop.txt"
    else
        echo "  nothing to prune"
    fi
fi

echo "regenerating index.html"
rclone lsf "$R2/$R2_PATH" --files-only --format "ps" --separator " " |
    grep '\.rpm ' > "$STAGE/files.txt"
python3 scripts/gen_repo_index.py "$STAGE/files.txt" "$STAGE/index.html" \
    "$TENKO_RELEASE" "$URL" "$REPO_ID"
rclone copyto "$STAGE/index.html" "$R2/$R2_PATH/index.html" --s3-no-check-bucket

if [ "$MIRROR" != "0" ]; then
    echo "mirroring to $MIRROR:$MIRROR_PUBLIC/packages/$TENKO_RELEASE/"
    ssh "$MIRROR" "mkdir -p $MIRROR_PUBLIC/packages/$TENKO_RELEASE/repodata"
    rsync -av -e "ssh" "${rpms[@]}" "$MIRROR:$MIRROR_PUBLIC/packages/$TENKO_RELEASE/"
    if [ "$PRUNE" = 1 ] && [ -s "$STAGE/keep.txt" ]; then
        echo "pruning mirror RPMs the merged metadata does not reference"
        ssh "$MIRROR" "cd $MIRROR_PUBLIC/packages/$TENKO_RELEASE && ls *.rpm" |
            while read -r name; do
                grep -qxF "$name" "$STAGE/keep.txt" || echo "$name"
            done > "$STAGE/mirror-drop.txt"
        if [ -s "$STAGE/mirror-drop.txt" ]; then
            sed 's/^/  drop /' "$STAGE/mirror-drop.txt"
            ssh "$MIRROR" \
                "cd $MIRROR_PUBLIC/packages/$TENKO_RELEASE && xargs rm -f" \
                < "$STAGE/mirror-drop.txt"
        else
            echo "  nothing to prune"
        fi
    fi
    rsync -av --delete -e "ssh" "$STAGE/merged/repodata/" \
        "$MIRROR:$MIRROR_PUBLIC/packages/$TENKO_RELEASE/repodata/"
    rsync -av -e "ssh" "$STAGE/index.html" \
        "$MIRROR:$MIRROR_PUBLIC/packages/$TENKO_RELEASE/index.html"
fi

echo
echo "published:"
for rpm in "${rpms[@]}"; do
    echo "  $(basename "$rpm")"
done
echo "verify: dnf --refresh -y --disablerepo='*' --repofrompath=t,$URL list --available <package>"
echo "repo:   $URL"
