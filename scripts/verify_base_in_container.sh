#!/usr/bin/env bash
# Rebuild the whole Browneye base package set inside the base container.
#
# This is the self-hosting check: the host only prepares the package list and
# bind mounts specs/sources/output.  Every rpmbuild invocation, including the
# compiler, make, Python, meson, systemd, and the RPM toolchain, runs inside
# localhost/browneye/base:r13.1.
set -euo pipefail
cd "$(dirname "$0")/.."

IMAGE=${IMAGE:-localhost/browneye/base:r13.1}
OUT=${OUT:-build/container-rebuild-$(date +%Y%m%d-%H%M%S)}
JOBS=${JOBS:-4}
MAKE_JOBS=${MAKE_JOBS:-4}

mkdir -p "$OUT"

python3 - "$OUT/packages.txt" <<'PY'
import glob
import json
import os
import sys

out = sys.argv[1]
with open("lfs.lock", encoding="utf-8") as handle:
    lock = json.load(handle)
aliases = lock.get("aliases", {})

# ORDER is the LFS r13.1 chapter-8 list plus bootstrap extras and glue.
with open("package_specs/ORDER", encoding="utf-8") as handle:
    names = [line.split("#", 1)[0].strip() for line in handle]
names = [name for name in names if name]
# browneye-base pulls these in, but ORDER does not list them.
names += ["libbsd", "libmd", "libseccomp", "browneye-base"]

seen = set()
rows = []
for name in names:
    directory = aliases.get(name, name)
    if directory in seen:
        continue
    seen.add(directory)
    canonical = os.path.join("package_specs", directory, directory + ".spec")
    if os.path.isfile(canonical):
        specs = [canonical]
    else:
        specs = sorted(glob.glob(os.path.join("package_specs", directory, "*.spec")))
    if not specs:
        print("warning: no spec for {} ({})".format(name, directory), file=sys.stderr)
        continue
    for spec in specs:
        rows.append(os.path.relpath(spec, "package_specs"))

with open(out, "w", encoding="utf-8") as handle:
    handle.write("\n".join(rows) + "\n")
print("packages: {}".format(len(rows)))
PY

cat "$OUT/packages.txt"

podman run --rm --network=none \
    -e JOBS="$JOBS" -e MAKE_JOBS="$MAKE_JOBS" \
    -v "$PWD/package_specs:/specs:ro,z" \
    -v "$HOME/rpmbuild/SOURCES:/sources:ro,z" \
    -v "$PWD/scripts/container_build_base.sh:/container_build_base.sh:ro,z" \
    -v "$PWD/$OUT:/out:rw,z" \
    "$IMAGE" /usr/bin/bash /container_build_base.sh

echo
echo "results: $PWD/$OUT"
echo "logs:    $PWD/$OUT/logs"
echo "rpms:    $PWD/$OUT/build/<package>/RPMS"
