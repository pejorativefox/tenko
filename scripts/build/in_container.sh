#!/usr/bin/env bash
# Run inside the Tenko base container.  Build every spec listed in
# /out/packages.txt with rpmbuild, keeping per-package logs and RPMs.
#
# The host side (scripts/build/specs.sh, `tenko build`) writes packages.txt
# and mounts this script.  This script intentionally uses only tooling that is
# present in the base image, except that it bootstraps pip from Python's
# bundled ensurepip before building the Python module specs.
set -uo pipefail

OUT=${OUT:-/out}
SPECS=${SPECS:-/specs}
SOURCES=${SOURCES:-/sources}
JOBS=${JOBS:-4}
MAKE_JOBS=${MAKE_JOBS:-4}

mkdir -p "$OUT"/{build,logs,rpms,status}

if [ ! -s "$OUT/packages.txt" ]; then
    echo "missing $OUT/packages.txt" >&2
    exit 2
fi

# The image deliberately does not ship pip yet (python was built with
# --without-ensurepip).  ensurepip is bundled with Python, so this is still
# an offline bootstrap from the base image itself.
if ! python3 -m pip --version >"$OUT/logs/ensurepip.log" 2>&1; then
    if ! python3 -m ensurepip --upgrade >>"$OUT/logs/ensurepip.log" 2>&1; then
        echo "failed to bootstrap pip" >&2
        cat "$OUT/logs/ensurepip.log" >&2
        exit 3
    fi
fi
python3 -m pip --version >>"$OUT/logs/ensurepip.log" 2>&1 || true

# Offline, reproducible pip behavior:
#   - do not create isolated build envs that try to reach PyPI
#   - ignore the copy already installed by rpm (we are installing into a
#     buildroot, not upgrading the running system)
export PIP_NO_BUILD_ISOLATION=1
export PIP_IGNORE_INSTALLED=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

build_one() {
    local rel=$1
    local pkg top rc start end rpms
    pkg=$(basename "$rel" .spec)
    top="$OUT/build/$pkg"

    if [ -f "$OUT/status/$pkg" ] && grep -q '^ok ' "$OUT/status/$pkg"; then
        return 0
    fi

    mkdir -p "$top"/{BUILD,BUILDROOT,RPMS,SRPMS,SPECS}
    export PIP_CACHE_DIR="$OUT/build/$pkg/pip-cache"

    start=$(date +%s)
    rpmbuild -bb --nodeps \
        --define "_topdir $top" \
        --define "_sourcedir $SOURCES" \
        --define "_smp_mflags -j$MAKE_JOBS" \
        --define "_smp_build_ncpus $MAKE_JOBS" \
        "$SPECS/$rel" >"$OUT/logs/$pkg.log" 2>&1
    rc=$?
    end=$(date +%s)

    rpms=$(find "$top/RPMS" -type f -name '*.rpm' -printf '%f ' 2>/dev/null)
    if [ "$rc" -eq 0 ]; then
        printf 'ok %s %ss %s\n' "$pkg" "$((end - start))" "$rpms" >"$OUT/status/$pkg"
        # Keep failed trees for diagnosis; successful trees are just disk.
        rm -rf "$top/BUILD" "$top/BUILDROOT" "$top/pip-cache"
    else
        printf 'fail %s %ss\n' "$pkg" "$((end - start))" >"$OUT/status/$pkg"
    fi
    return 0
}

running=0
while IFS= read -r rel; do
    rel=${rel%%#*}
    rel=${rel#"${rel%%[![:space:]]*}"}
    rel=${rel%"${rel##*[![:space:]]}"}
    [ -n "$rel" ] || continue
    build_one "$rel" &
    running=$((running + 1))
    if [ "$running" -ge "$JOBS" ]; then
        wait -n || true
        running=$((running - 1))
    fi
done <"$OUT/packages.txt"
wait || true

echo "=== summary ==="
cat "$OUT"/status/* 2>/dev/null | sort
echo "=== counts ==="
awk '{print $1}' "$OUT"/status/* 2>/dev/null | sort | uniq -c
