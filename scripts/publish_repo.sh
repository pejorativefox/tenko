#!/usr/bin/env bash
# Stage and publish the Browneye RPM repository to tomfool.8bit.ca.
#
# Publishes the single Browneye repository (base + desktop).
#
# Usage:
#   scripts/publish_repo.sh                     # version 13.1 from build/repo-all
#   RSYNC_OPTS=-c scripts/publish_repo.sh       # checksum mode (changed files only)
#   VERSION=13.1 REPO=build/repo-all scripts/publish_repo.sh
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION=${VERSION:-13.1}
REPO=${REPO:-build/repo-all}
REPO_ID=browneye-$VERSION
STAGE=${STAGE:-build/repo-publish/$VERSION}
REMOTE=${REMOTE:-tomfool8@192.200.112.194}
PORT=${PORT:-53211}
PUBLIC=${PUBLIC:-public_html/browneye}
DEST=${DEST:-$PUBLIC/packages/$VERSION/}
URL=${URL:-https://tomfool.8bit.ca/browneye/packages/$VERSION/}
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

  curl -o /etc/yum.repos.d/$REPO_ID.repo \\
    ${URL}$REPO_ID.repo

Or use it directly:

  dnf --repofrompath=browneye,$URL \\
      --disablerepo='*' install browneye-base

The desktop is in the same repository:

  dnf --repofrompath=browneye,$URL \\
      --disablerepo='*' install xfce-desktop

The repository is unsigned; gpgcheck is disabled.
EOF

echo "staged $rpm_count RPMs in $STAGE"

# Generate a package listing because the web server has directory indexes off.
python3 - "$STAGE" "$VERSION" "$URL" "$REPO_ID" <<'PY'
import html
import os
import sys

stage, version, url, repo_id = sys.argv[1:5]
rpms = sorted(f for f in os.listdir(stage) if f.endswith(".rpm"))
rows = []
for name in rpms:
    size = os.path.getsize(os.path.join(stage, name))
    rows.append(
        '        <tr><td><a href="{}">{}</a></td><td>{:.1f} MB</td></tr>'.format(
            html.escape(name), html.escape(name), size / 1048576.0
        )
    )

page = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Browneye Linux {version} — packages</title>
<style>
 body {{ margin:0; background:#faf7f2; color:#2a211a;
        font:16px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }}
 .wrap {{ max-width:900px; margin:0 auto; padding:36px 22px 60px; }}
 h1 {{ font-size:26px; margin:0 0 6px; }}
 p {{ color:#6f6257; margin:0 0 18px; }}
 a {{ color:#8a4b1e; }}
 table {{ width:100%; border-collapse:collapse; background:#fff;
          border:1px solid #e6ddd2; border-radius:10px; overflow:hidden; }}
 th, td {{ text-align:left; padding:10px 14px; border-bottom:1px solid #e6ddd2;
           font-size:14px; }}
 th {{ background:#f3e6d8; font-size:12px; text-transform:uppercase;
       letter-spacing:.08em; color:#6b4a2f; }}
 td:last-child {{ white-space:nowrap; color:#6f6257; }}
 tr:last-child td {{ border-bottom:0; }}
 code {{ font-family:ui-monospace,monospace; }}
</style>
</head>
<body><div class="wrap">
<h1>Browneye Linux {version} — packages</h1>
<p><a href="../../">&larr; repository overview</a> · {count} RPMs ·
   <a href="{repo_id}.repo">{repo_id}.repo</a> ·
   <a href="../../iso/browneye-installer.iso">installer ISO</a></p>
<table>
  <thead><tr><th>Package</th><th>Size</th></tr></thead>
  <tbody>
{rows}
  </tbody>
</table>
</div></body></html>
""".format(version=version, repo_id=repo_id, count=len(rpms), rows="\n".join(rows))

with open(os.path.join(stage, "index.html"), "w", encoding="utf-8") as handle:
    handle.write(page)
PY

if [ "$DRY_RUN" = 1 ]; then
    echo "dry run: staged $rpm_count RPMs in $STAGE; not uploading"
    exit 0
fi

ssh -p "$PORT" "$REMOTE" "mkdir -p ~/$PUBLIC/packages"
rsync -av $RSYNC_OPTS --delete -e "ssh -p $PORT" "$STAGE/" "$REMOTE:$DEST"
if [ -f "$INDEX" ]; then
    rsync -av -e "ssh -p $PORT" "$INDEX" "$REMOTE:$PUBLIC/index.html"
fi
echo "published $URL"
