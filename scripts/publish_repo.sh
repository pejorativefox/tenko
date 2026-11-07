#!/usr/bin/env bash
# Stage and publish the Tenko RPM repository to the public R2 bucket
# (the LAN mirror is refreshed too).
#
# Publishes the single Tenko repository (base + desktop).
#
# Usage:
#   scripts/publish_repo.sh                     # Tenko 6 from build/repo-all
#   RSYNC_OPTS=-c scripts/publish_repo.sh       # checksum mode (changed files only)
#   TENKO_RELEASE=6 REPO=build/repo-all scripts/publish_repo.sh
set -euo pipefail
cd "$(dirname "$0")/.."

TENKO_RELEASE=${TENKO_RELEASE:-6}
REPO=${REPO:-build/repo-all}
REPO_ID=tenko-$TENKO_RELEASE
STAGE=${STAGE:-build/repo-publish/$TENKO_RELEASE}
# Cloudflare R2 (S3) target; the new Tenko bucket is r2_tenko:tenko; r2:browneye remains the compatibility alias.
# The old r2:browneye/packages/13.1 tree remains the external compatibility alias.
R2=${R2:-r2_tenko:tenko}
R2_PATH=${R2_PATH:-packages/$TENKO_RELEASE}
# LAN mirror; set MIRROR=0 to skip. The old public_html/browneye symlink
# remains the external compatibility alias.
MIRROR=${MIRROR:-daspork@192.168.31.9}
MIRROR_PUBLIC=${MIRROR_PUBLIC:-public_html/tenko}
URL=${URL:-https://tenko.pjfox.xyz/packages/$TENKO_RELEASE/}
INDEX=${INDEX:-web/index.html}
RSYNC_OPTS=${RSYNC_OPTS:-}
DRY_RUN=${DRY_RUN:-0}

[ -d "$REPO" ] || { echo "missing repo directory: $REPO" >&2; exit 1; }
rpm_count=$(find "$REPO" -maxdepth 1 -name '*.rpm' | wc -l)
[ "$rpm_count" -gt 0 ] || { echo "no RPMs in $REPO" >&2; exit 1; }

rm -rf "$STAGE"
mkdir -p "$STAGE"
# -p keeps RPM mtimes so repeated publishes only re-upload changed files.
cp -p "$REPO"/*.rpm "$STAGE"/
createrepo_c --quiet "$STAGE"

cat > "$STAGE/$REPO_ID.repo" <<EOF
[$REPO_ID]
name=Tenko Linux $TENKO_RELEASE
baseurl=$URL
enabled=1
gpgcheck=0
repo_gpgcheck=0
EOF

cat > "$STAGE/README.txt" <<EOF
Tenko Linux $TENKO_RELEASE package repository

  baseurl: $URL

Install the repo definition:

  curl -o /etc/yum.repos.d/$REPO_ID.repo \\
    ${URL}$REPO_ID.repo

Or use it directly:

  dnf --repofrompath=tenko,$URL \\
      --disablerepo='*' install tenko-base

The desktop is in the same repository:

  dnf --repofrompath=tenko,$URL \\
      --disablerepo='*' install xfce-desktop

The repository is unsigned; gpgcheck is disabled.
EOF

echo "staged $rpm_count RPMs in $STAGE"

# Generate a package listing because the web server has directory indexes off.
# gen_repo_index.py owns the markup; publish_rpm.sh uses the same template.
INDEX_LISTING=${INDEX_LISTING:-build/repo-index-files-$TENKO_RELEASE.txt}
find "$STAGE" -maxdepth 1 -name '*.rpm' -printf '%f %s\n' | sort > "$INDEX_LISTING"
python3 scripts/gen_repo_index.py "$INDEX_LISTING" "$STAGE/index.html" \
    "$TENKO_RELEASE" "$URL" "$REPO_ID"

if [ "$DRY_RUN" = 1 ]; then
    echo "dry run: staged $rpm_count RPMs in $STAGE; not uploading"
    exit 0
fi

rclone sync "$STAGE/" "$R2/$R2_PATH" --transfers 8 --s3-no-check-bucket
if [ -f "$INDEX" ]; then
    rclone copyto "$INDEX" "$R2/index.html" --s3-no-check-bucket
fi

if [ "$MIRROR" != "0" ]; then
    echo "mirroring to $MIRROR:$MIRROR_PUBLIC"
    ssh "$MIRROR" "mkdir -p $MIRROR_PUBLIC/packages/$TENKO_RELEASE"
    rsync -av $RSYNC_OPTS --delete -e "ssh" "$STAGE/" \
        "$MIRROR:$MIRROR_PUBLIC/packages/$TENKO_RELEASE/"
    if [ -f "$INDEX" ]; then
        rsync -av -e "ssh" "$INDEX" "$MIRROR:$MIRROR_PUBLIC/index.html"
    fi
fi
echo "published $URL"
