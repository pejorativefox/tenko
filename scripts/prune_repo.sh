#!/usr/bin/env bash
# Keep only the newest version of each package in an RPM repository.
#
# Uses rpm's own version comparison (python3-rpm) instead of the optional
# rpmdev-vercmp tool, which is not installed on the Browneye host.  The old
# rpmdev fallback silently deleted every newer package when the tool was
# missing.
set -euo pipefail
repo=${1:?repo directory}
[ -d "$repo" ] || exit 0

python3 - "$repo" <<'PY'
import glob
import os
import subprocess
import sys

import rpm

repo = sys.argv[1]
query = "%{NAME}\t%{ARCH}\t%{EPOCHNUM}\t%{VERSION}\t%{RELEASE}"
best = {}

for path in sorted(glob.glob(os.path.join(repo, "*.rpm"))):
    try:
        out = subprocess.check_output(
            ["rpm", "-qp", "--qf", query, path], text=True,
            stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        continue
    if not out or "\t" not in out:
        continue
    name, arch, epoch, version, release = out.split("\t")
    if not name:
        continue
    key = (name, arch)
    candidate = (epoch or "0", version, release)
    if key not in best:
        best[key] = (candidate, path)
        continue
    comparison = rpm.labelCompare(candidate, best[key][0])
    if comparison > 0:
        os.unlink(best[key][1])
        best[key] = (candidate, path)
    elif comparison < 0:
        os.unlink(path)
    # Equal EVR: keep both.  A repeated NEVRA with different content is
    # refused later by publish_rpm.sh/publish_repo.sh, not silently dropped.
PY
