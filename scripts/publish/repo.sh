#!/usr/bin/env bash
# Stage and publish the Tenko RPM repository to the public R2 bucket
# (the LAN mirror is refreshed too).
#
# This replaces the whole published repository with the RPMs in REPO
# (rclone sync and rsync --delete): anything not in REPO disappears.  For
# normal package updates use `tenko publish rpm`, which merges into the
# published metadata instead.
#
# Usage:
#   REPO=build/repo tenko publish repo
#   RSYNC_OPTS=-c REPO=build/repo tenko publish repo   # mirror: checksum mode
#   DRY_RUN=1 REPO=build/repo tenko publish repo       # stage only
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
. scripts/lib/publish.sh

REPO=${REPO:-}
STAGE=${STAGE:-build/repo-publish/$TENKO_RELEASE}
INDEX=${INDEX:-web/index.html}
RSYNC_OPTS=${RSYNC_OPTS:-}

[ -n "$REPO" ] || die "set REPO to a directory of RPMs (see tenko publish repo --help)"
[ -d "$REPO" ] || die "missing repo directory: $REPO"
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
# repo_index.py owns the markup; `tenko publish rpm` uses the same template.
INDEX_LISTING=${INDEX_LISTING:-build/repo-index-files-$TENKO_RELEASE.txt}
find "$STAGE" -maxdepth 1 -name '*.rpm' -printf '%f %s\n' | sort > "$INDEX_LISTING"
python3 scripts/publish/repo_index.py "$INDEX_LISTING" "$STAGE/index.html" \
    "$TENKO_RELEASE" "$URL" "$REPO_ID"

if [ "$DRY_RUN" = 1 ]; then
    echo "dry run: staged $rpm_count RPMs in $STAGE; not uploading"
    exit 0
fi

rclone sync "$STAGE/" "$R2/$REPO_PATH" --transfers 8 --s3-no-check-bucket
if [ -f "$INDEX" ]; then
    rclone copyto "$INDEX" "$R2/index.html" --s3-no-check-bucket
fi

if mirror_enabled; then
    echo "mirroring to $MIRROR:$MIRROR_PUBLIC"
    mirror_mkdir "$REPO_PATH"
    rsync -av $RSYNC_OPTS --delete -e "ssh" "$STAGE/" \
        "$MIRROR:$MIRROR_PUBLIC/$REPO_PATH/"
    if [ -f "$INDEX" ]; then
        rsync -av -e "ssh" "$INDEX" "$MIRROR:$MIRROR_PUBLIC/index.html"
    fi
fi
echo "published $URL"
