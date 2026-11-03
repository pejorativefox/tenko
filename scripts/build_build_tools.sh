#!/usr/bin/env bash
# Build the self-hosted repo/rootfs assembly toolchain (E1):
# dnf + libdnf + createrepo_c and their dependency stack, inside the
# self-hosted base image and without network access.
#
# The host only prepares the source/filelist directory, mounts it read-only
# and runs rpmbuild in the container.  Each package is installed into the
# persistent container as soon as it is built so the next package can see
# its headers and libraries.
#
# Usage:
#   scripts/build_build_tools.sh                 # all packages
#   PACKAGES="glib libxml2" scripts/build_build_tools.sh
#   FORCE=1 scripts/build_build_tools.sh dnf     # rebuild even if ok
#   KEEP=0 scripts/build_build_tools.sh          # fresh container
#
# Static filelists: when package_specs/<dir>/files/<pkg>.filelist is missing
# or empty, the package is first built with `_unpackaged_files_terminate_build
# 0`, the filelist is generated from BUILDROOT with
# scripts/gen_filelist_tree.py, and the package is rebuilt strictly with the
# generated list.  The generated list is written back into the worktree, so a
# second run is a normal strict build.  Entries that need %config flags (the
# dnf configuration files) are corrected by hand after generation.
set -uo pipefail
cd "$(dirname "$0")/.."

IMG=${IMG:-localhost/browneye/base:r13.1}
OUT=${OUT:-$PWD/build/e1/out}
SRC=${SRC:-$PWD/build/e1/srcroot}
TARBALLS=${TARBALLS:-$PWD/build/e1/sources}
CTR=${CTR:-browneye-e1}
PROGRESS_IMAGE=${PROGRESS_IMAGE:-localhost/browneye/e1-progress:latest}
JOBS=${JOBS:-8}
KEEP=${KEEP:-0}
FORCE=${FORCE:-0}

mkdir -p "$OUT"/{logs,status,build} "$SRC"

# Tarballs and static filelists share the container's %_sourcedir.
cp -n "$TARBALLS"/*.tar.* "$SRC"/ 2>/dev/null || true
for list in package_specs/*/files/*.filelist; do
    [ -f "$list" ] || continue
    cp -f "$list" "$SRC/$(basename "$list")"
done

if [ "$KEEP" != "1" ]; then
    podman rm -f "$CTR" >/dev/null 2>&1 || true
fi
if ! podman container exists "$CTR"; then
    if podman image exists "$PROGRESS_IMAGE" 2>/dev/null; then
        echo "resuming from $PROGRESS_IMAGE"
        base_image=$PROGRESS_IMAGE
    else
        base_image=$IMG
    fi
    podman run -d --name "$CTR" --network=none \
        -v "$PWD/package_specs:/specs:ro,z" \
        -v "$SRC:/sources:ro,z" \
        -v "$OUT:/out:rw,z" \
        "$base_image" sleep infinity >/dev/null
fi
podman start "$CTR" >/dev/null 2>&1 || true

# Commit the container after every package so an interrupted run (the
# container can be stopped by the environment) resumes with all previously
# installed dependencies instead of starting from the base image.
snapshot() {
    podman commit "$CTR" "$PROGRESS_IMAGE" >/dev/null 2>&1 || true
}

# Reinstall every package already marked ok, in build order.  The status
# files record builds, not the contents of the current container: a resumed
# container may come from an older snapshot (or from the base image), so the
# dependency prefixes must be restored before the next build.
resume_installs() {
    local top
    for top in $ALL_ORDER; do
        [ "$(status_of "$top")" = ok ] || continue
        ls "$OUT/build/$top"/RPMS/*/*.rpm >/dev/null 2>&1 || continue
        podman exec "$CTR" bash -lc \
            "rpm -Uvh --nodeps --replacepkgs --replacefiles /out/build/$top/RPMS/*/*.rpm && ldconfig" \
            >>"$OUT/logs/$top.log" 2>&1 || true
    done
    snapshot
}

status_of() { awk '{print $1}' "$OUT/status/$1" 2>/dev/null; }

# build <package-dir> <topdir> <spec-file-name> [rpmbuild --define ...]
build() {
    local dir=$1 top=$2 specfile=$3
    shift 3
    local spec=${specfile%.spec}
    local builds="$OUT/build/$top"
    local filelist="package_specs/$dir/files/$spec.filelist"
    local root
    local -a strict_def=()

    if [ "$FORCE" != 1 ] && [ "$(status_of "$top")" = ok ]; then
        echo "skip $top"
        return 0
    fi

    mkdir -p "$builds"/{BUILD,BUILDROOT,RPMS,SRPMS,SPECS}
    rm -rf "$builds"/RPMS/* "$builds"/BUILDROOT/*

    # Meta-packages (empty %files, no generated list) are built normally.
    if ! grep -q 'filelist' "package_specs/$dir/$specfile"; then
        if ! podman exec "$CTR" rpmbuild -bb --nodeps --noclean \
                --define "_topdir /out/build/$top" \
                --define "_sourcedir /sources" \
                --define "_smp_mflags -j$JOBS" \
                "$@" "/specs/$dir/$specfile" \
                >"$OUT/logs/$top.log" 2>&1; then
            echo "fail $top" | tee "$OUT/status/$top"
            tail -20 "$OUT/logs/$top.log" >&2
            return 1
        fi
        if ! podman exec "$CTR" bash -lc \
                "rpm -Uvh --nodeps --replacepkgs --replacefiles /out/build/$top/RPMS/x86_64/*.rpm && ldconfig" \
                >>"$OUT/logs/$top.log" 2>&1; then
            echo "fail $top (install)" | tee "$OUT/status/$top"
            tail -20 "$OUT/logs/$top.log" >&2
            return 1
        fi
        echo "ok $top" | tee "$OUT/status/$top"
        snapshot
        return 0
    fi

    if [ ! -s "$filelist" ]; then
        echo "bootstrap $top (generating static filelist)"
        # A non-empty placeholder is required: rpm treats an empty %files -f
        # file as an error.
        printf '%%dir /usr\n' > "$SRC/$spec.filelist"
        strict_def=(--define "_unpackaged_files_terminate_build 0")
    fi

    if ! podman exec "$CTR" rpmbuild -bb --nodeps --noclean \
            --define "_topdir /out/build/$top" \
            --define "_sourcedir /sources" \
            --define "_smp_mflags -j$JOBS" \
            "${strict_def[@]}" "$@" "/specs/$dir/$specfile" \
            >"$OUT/logs/$top.log" 2>&1; then
        echo "fail $top" | tee "$OUT/status/$top"
        tail -20 "$OUT/logs/$top.log" >&2
        return 1
    fi

    if [ "${#strict_def[@]}" -gt 0 ]; then
        # Rebuild the %files list from the populated buildroot.
        root=$(ls -d "$builds"/BUILDROOT/*/ 2>/dev/null | head -1)
        if [ -z "$root" ]; then
            echo "fail $top (empty buildroot)" | tee "$OUT/status/$top"
            return 1
        fi
        if ! python3 scripts/gen_filelist_tree.py --root "${root%/}" \
                --output "$filelist"; then
            echo "fail $top (filelist)" | tee "$OUT/status/$top"
            return 1
        fi
        cp -f "$filelist" "$SRC/"
        rm -rf "$builds"/RPMS/* "$builds"/BUILDROOT/*
        if ! podman exec "$CTR" rpmbuild -bb --nodeps --noclean \
                --define "_topdir /out/build/$top" \
                --define "_sourcedir /sources" \
                --define "_smp_mflags -j$JOBS" \
                "$@" "/specs/$dir/$specfile" \
                >"$OUT/logs/$top.log" 2>&1; then
            echo "fail $top (strict rebuild)" | tee "$OUT/status/$top"
            tail -20 "$OUT/logs/$top.log" >&2
            return 1
        fi
    fi

    if ! podman exec "$CTR" bash -lc \
            "rpm -Uvh --nodeps --replacepkgs --replacefiles /out/build/$top/RPMS/x86_64/*.rpm && ldconfig" \
            >>"$OUT/logs/$top.log" 2>&1; then
        if ! podman exec "$CTR" bash -lc \
                "rpm -Uvh --nodeps --replacepkgs --replacefiles --force /out/build/$top/RPMS/x86_64/*.rpm" \
                >>"$OUT/logs/$top.log" 2>&1; then
            echo "fail $top (install)" | tee "$OUT/status/$top"
            tail -20 "$OUT/logs/$top.log" >&2
            return 1
        fi
    fi

    echo "ok $top" | tee "$OUT/status/$top"
    snapshot
}

ALL_ORDER="
xz
pcre2
openssl
curl
libuv
cmake
python3-docutils
gobject-introspection
glib
libxml2
json-c
libgpg-error
libassuan
gpgme
swig
libyaml
zchunk
libsolv
libcomps
libmodulemd
librepo
rpm
libdnf
dnf
createrepo_c
browneye-build
"

# spec directory and spec file name for each entry in ALL_ORDER
spec_dir_of() {
    case $1 in
        libmodulemd) echo "libmodulemd libmodulemd" ;;
        *) echo "$1 $1" ;;
    esac
}

LIST=${PACKAGES:-$ALL_ORDER}
resume_installs
for top in $LIST; do
    read -r dir spec <<<"$(spec_dir_of "$top")"
    build "$dir" "$top" "$spec.spec" || exit 1
done
snapshot

echo "=== summary ==="
cat "$OUT"/status/* 2>/dev/null | sort
