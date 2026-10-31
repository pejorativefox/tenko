#!/usr/bin/env bash
# Stage and publish the Browneye RPM repository to tomfool.8bit.ca.
#
# Usage:
#   scripts/publish_repo.sh                 # version 13.1 from build/repo-selfhost
#   VERSION=13.1 REPO=build/repo-selfhost scripts/publish_repo.sh
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION=${VERSION:-13.1}
REPO=${REPO:-build/repo-selfhost}
STAGE=${STAGE:-build/repo-publish/$VERSION}
REMOTE=${REMOTE:-tomfool8@192.200.112.194}
PORT=${PORT:-53211}
PUBLIC=${PUBLIC:-public_html/browneye}
DEST=${DEST:-$PUBLIC/packages/$VERSION/}
URL=${URL:-https://tomfool.8bit.ca/browneye/packages/$VERSION/}
INDEX=${INDEX:-web/index.html}

[ -d "$REPO" ] || { echo "missing repo directory: $REPO" >&2; exit 1; }
rpm_count=$(find "$REPO" -maxdepth 1 -name '*.rpm' | wc -l)
[ "$rpm_count" -gt 0 ] || { echo "no RPMs in $REPO" >&2; exit 1; }

rm -rf "$STAGE"
mkdir -p "$STAGE"
# -p keeps RPM mtimes so repeated publishes only re-upload changed files.
cp -p "$REPO"/*.rpm "$STAGE"/
createrepo_c --quiet "$STAGE"

cat > "$STAGE/browneye-$VERSION.repo" <<EOF
[browneye-$VERSION]
name=Browneye Linux $VERSION
baseurl=$URL
enabled=1
gpgcheck=0
repo_gpgcheck=0
EOF

cat > "$STAGE/README.txt" <<EOF
Browneye Linux $VERSION package repository

  baseurl: $URL

Install the repo definition:

  curl -o /etc/yum.repos.d/browneye-$VERSION.repo \\
    ${URL}browneye-$VERSION.repo

Or use it directly:

  dnf --repofrompath=browneye,$URL \\
      --disablerepo='*' install browneye-base

The repository is unsigned; gpgcheck is disabled.
EOF

echo "staged $rpm_count RPMs in $STAGE"
ssh -p "$PORT" "$REMOTE" "mkdir -p ~/$PUBLIC/packages"
rsync -av --delete -e "ssh -p $PORT" "$STAGE/" "$REMOTE:$DEST"
if [ -f "$INDEX" ]; then
    rsync -av -e "ssh -p $PORT" "$INDEX" "$REMOTE:$PUBLIC/index.html"
fi
echo "published $URL"
