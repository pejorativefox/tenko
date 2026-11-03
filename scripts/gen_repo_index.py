#!/usr/bin/env python3
"""Render the package index.html for the Browneye RPM repository.

Usage:
    gen_repo_index.py LISTING OUTPUT VERSION URL REPO_ID

LISTING is a file of "name size" lines (for example the output of
    ssh host 'cd repo && find . -maxdepth 1 -name "*.rpm" -printf "%f %s\\n"')
so the index can be regenerated from the published repository itself, without
a local copy of the RPMs.

The markup matches what scripts/publish_repo.sh wrote before this helper
existed; the repository has directory indexes off, so this page is the only
listing users get.
"""
import html
import sys
from pathlib import Path

PAGE = """<!DOCTYPE html>
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
   <a href="../../iso/browneye-installer.iso">installer ISO</a> ·
   <a href="../../rootfs/browneye-rootfs.tar.gz">container rootfs</a></p>
<table>
  <thead><tr><th>Package</th><th>Size</th></tr></thead>
  <tbody>
{rows}
  </tbody>
</table>
</div></body></html>
"""


def main():
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    listing, output, version, url, repo_id = sys.argv[1:]
    entries = []
    for line in Path(listing).read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) != 2 or not fields[0].endswith(".rpm"):
            continue
        entries.append((fields[0], int(fields[1])))
    entries.sort()
    rows = "\n".join(
        '        <tr><td><a href="{}">{}</a></td><td>{:.1f} MB</td></tr>'.format(
            html.escape(name), html.escape(name), size / 1048576.0)
        for name, size in entries)
    page = PAGE.format(version=version, repo_id=repo_id,
                       count=len(entries), rows=rows)
    Path(output).write_text(page, encoding="utf-8")
    print("wrote {}: {} RPMs".format(output, len(entries)))


if __name__ == "__main__":
    main()
