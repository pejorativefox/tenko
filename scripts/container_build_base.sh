#!/usr/bin/env bash
# Run inside the Browneye base container.  Build every spec listed in
# /out/packages.txt with rpmbuild, keeping per-package logs and RPMs.
#
# The host wrapper scripts/verify_base_in_container.sh creates packages.txt
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

# texinfo is a bootstrap package: the image's old texinfo was built on the
# host against Perl 5.42, while the container ships Perl 5.44.  Its MiscXS.so
# fails to load, breaking every later build that invokes makeinfo.  Rebuild
# texinfo first with the container's Perl and install that RPM into the
# throw-away container before scheduling the rest.
if grep -qx 'texinfo/texinfo.spec' "$OUT/packages.txt"; then
    echo "prebuilding texinfo bootstrap"
    build_one texinfo/texinfo.spec
    if grep -q '^ok ' "$OUT/status/texinfo" 2>/dev/null; then
        tex_rpm=$(find "$OUT/build/texinfo/RPMS" -type f -name 'texinfo-*.rpm' | head -1)
        if [ -n "$tex_rpm" ]; then
            rpm -Uvh --replacepkgs --replacefiles --nodeps "$tex_rpm" \
                >"$OUT/logs/texinfo-install.log" 2>&1 || true
            if makeinfo --version >>"$OUT/logs/texinfo-install.log" 2>&1; then
                echo "texinfo bootstrap installed"
            else
                echo "warning: rebuilt texinfo did not load cleanly" >&2
            fi
        fi
    fi
fi

# sqlite's autosetup configure script needs a working tclsh.  The image's
# old tcl was installed with a host-style /usr/lib/tcl8.6 path, while the
# rebuilt tcl lives under /usr/lib64/lib/tcl8.6.  Rebuild tcl first and
# install it, including its compatibility symlinks.
if grep -qx 'tcl/tcl.spec' "$OUT/packages.txt"; then
    echo "prebuilding tcl bootstrap"
    build_one tcl/tcl.spec
    if grep -q '^ok ' "$OUT/status/tcl" 2>/dev/null; then
        tcl_rpm=$(find "$OUT/build/tcl/RPMS" -type f -name 'tcl-*.rpm' | head -1)
        if [ -n "$tcl_rpm" ]; then
            rpm -Uvh --replacepkgs --replacefiles --nodeps "$tcl_rpm" \
                >"$OUT/logs/tcl-install.log" 2>&1 || true
            if tclsh -c 'puts OK' >>"$OUT/logs/tcl-install.log" 2>&1; then
                echo "tcl bootstrap installed"
            else
                echo "warning: rebuilt tcl did not load cleanly" >&2
            fi
        fi
    fi
fi

# btrfs-progs needs liblzo2 headers and libraries at configure time.  Build
# and install liblzo2 before the parallel wave so btrfs-progs does not race
# an uninstalled dependency (the base image does not ship lzo).
needs_lzo=0
if grep -qx 'btrfs-progs/btrfs-progs.spec' "$OUT/packages.txt"; then
    needs_lzo=1
fi
if grep -qx 'liblzo2/liblzo2.spec' "$OUT/packages.txt"; then
    needs_lzo=1
fi
if [ "$needs_lzo" = 1 ] && [ -f "$SPECS/liblzo2/liblzo2.spec" ]; then
    echo "prebuilding liblzo2 bootstrap"
    build_one liblzo2/liblzo2.spec
    if grep -q '^ok ' "$OUT/status/liblzo2" 2>/dev/null; then
        lzo_rpm=$(find "$OUT/build/liblzo2/RPMS" -type f -name 'liblzo2-*.rpm' | head -1)
        if [ -n "$lzo_rpm" ]; then
            rpm -Uvh --replacepkgs --replacefiles --nodeps "$lzo_rpm" \
                >"$OUT/logs/liblzo2-install.log" 2>&1 || true
            if [ -f /usr/include/lzo/lzo1x.h ]; then
                echo "liblzo2 bootstrap installed"
            else
                echo "warning: liblzo2 headers are still missing" >&2
            fi
        fi
    fi
fi

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
