#!/usr/bin/env bash
# Build the X11 client utilities wave: 31 spec dirs updated to BLFS r13.1,
# built inside Tenko base containers without network access.
#
# Toolchain: localhost/tenko/build-htop:13.1 (tenko-base + gcc/rpm).
# Build dependencies (published X11 libs) are staged from the public repo in
# ~/rpmbuild/SOURCES/x11deps and baked into a deps image that every worker
# slot shares.  Tarballs are staged with scripts/sync_blfs_spec.py --stage
# (md5-verified against the book).
#
# WORKERS=1 (default 1) builds everything sequentially in one persistent
# container.  WORKERS=N builds N packages at a time across N short-lived
# slots, each seeded with the deps image and every already-built wave RPM.
#
# Usage:
#   WORKERS=6 scripts/build_x11_utils.sh                 # parallel, 31 pkgs
#   PACKAGES="xev xrandr" WORKERS=2 scripts/build_x11_utils.sh
#   FORCE=1 WORKERS=1 scripts/build_x11_utils.sh xev     # rebuild one
set -uo pipefail
cd "$(dirname "$0")/.."
. scripts/repo_tools.sh

IMG=${IMG:-$(pick_image localhost/tenko/build-htop:13.1 localhost/browneye/build-htop:13.1)}
OUT=${OUT:-$PWD/build/x11-wave/out}
CTR=${CTR:-tenko-x11}
DEPS_IMAGE=${DEPS_IMAGE:-$(pick_image localhost/tenko/x11-deps:latest localhost/browneye/x11-deps:latest)}
JOBS=${JOBS:-8}
WORKERS=${WORKERS:-1}
FORCE=${FORCE:-0}

ORDER="
xbitmaps
xcursorgen
libxpm
libxaw
libxv
luit
bdftopcf
sessreg
setxkbmap
smproxy
xcmsdb
xdpyinfo
xdriinfo
xev
xgamma
xinput
xkbevd
xkbutils
xkill
xlsatoms
xlsclients
xmessage
xpr
xprop
xrandr
xrefresh
xsetroot
xvinfo
xwud
xterm
xcursor-themes
"

mkdir -p "$OUT"/{logs,status,build}

# Static filelists for the generated wave specs live in
# package_specs/<dir>/files/<pkg>.filelist; they share %_sourcedir with the
# tarballs (~/rpmbuild/SOURCES).
LIST_ALL=${PACKAGES:-$ORDER}
for list in $LIST_ALL; do
    if [ -f "package_specs/$list/files/$list.filelist" ]; then
        cp -f "package_specs/$list/files/$list.filelist" \
              "$HOME/rpmbuild/SOURCES/$list.filelist"
    elif ! [ -s "$HOME/rpmbuild/SOURCES/$list.filelist" ]; then
        # bootstrap placeholder: a real run generates the true list
        printf '%%dir /usr\n' > "$HOME/rpmbuild/SOURCES/$list.filelist"
    fi
done

status_of() { awk '{print $1}' "$OUT/status/$1" 2>/dev/null; }

# RPMs of every already-built package, into a slot's fresh filesystem.
pending() {
    for top in $LIST; do
        [ "$FORCE" != 1 ] && [ "$(status_of "$top")" = ok ] && continue
        printf '%s\n' "$top"
    done
}

# Bake build dependencies once: install the staged dependency RPMs plus
# llvm-libs into a throwaway container, then commit it as DEPS_IMAGE so
# every slot starts without re-installing anything.
make_deps_image() {
    if podman image exists "$DEPS_IMAGE"; then
        return 0
    fi
    local tmp=${CTR}-setup
    podman rm -f "$tmp" >/dev/null 2>&1 || true
    podman run -d --name "$tmp" --network=none \
        -v "$HOME/rpmbuild/SOURCES:/sources:ro,z" \
        "$IMG" sleep infinity >/dev/null
    podman exec "$tmp" bash -lc \
        "rpm -Uvh --nodeps --replacepkgs --replacefiles /sources/x11deps/*.rpm
         ldconfig
         test -e /usr/lib64/libGL.so && echo deps-ok" \
        >"$OUT/logs/deps-install.log" 2>&1 \
        || { echo "dependency install failed (see $OUT/logs/deps-install.log)" >&2;
             podman rm -f "$tmp" >/dev/null 2>&1 || true
             exit 1; }
    grep -q deps-ok "$OUT/logs/deps-install.log" \
        || { echo "deps-install did not complete cleanly (no GL)" >&2; exit 1; }
    podman commit "$tmp" "$DEPS_IMAGE" >/dev/null
    podman rm -f "$tmp" >/dev/null 2>&1 || true
}

# One build() per package.  All state is shared: status and logs in $OUT.
# base_image differs per slot: DEPS_IMAGE with wire RPMs already installed.
build() {
    local ctr=$1 dir=$2 top=$3 specfile=$4
    shift 4
    local spec=${specfile%.spec}
    local builds="$OUT/build/$top"
    local filelist="package_specs/$dir/files/$spec.filelist"
    local src_filelist="$HOME/rpmbuild/SOURCES/$spec.filelist"
    local root
    local -a strict_def=()

    mkdir -p "$builds"/{BUILD,BUILDROOT,RPMS,SRPMS,SPECS}
    rm -rf "$builds"/RPMS/* "$builds"/BUILDROOT/*

    if [ ! -s "$filelist" ]; then
        echo "[$ctr] bootstrap $top (generating static filelist)"
        printf '%%dir /usr\n' > "$src_filelist"
        strict_def=(--define "_unpackaged_files_terminate_build 0")
    fi

    if ! podman exec "$ctr" rpmbuild -bb --nodeps --noclean \
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
        cp -f "$filelist" "$src_filelist"
        rm -rf "$builds"/RPMS/* "$builds"/BUILDROOT/*
        if ! podman exec "$ctr" rpmbuild -bb --nodeps --noclean \
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

    if ! podman exec "$ctr" bash -lc \
            "rpm -Uvh --nodeps --replacepkgs --replacefiles /out/build/$top/RPMS/x86_64/*.rpm && ldconfig" \
            >>"$OUT/logs/$top.log" 2>&1; then
        if ! podman exec "$ctr" bash -lc \
                "rpm -Uvh --nodeps --replacepkgs --replacefiles --force /out/build/$top/RPMS/x86_64/*.rpm" \
                >>"$OUT/logs/$top.log" 2>&1; then
            echo "fail $top (install)" | tee "$OUT/status/$top"
            return 1
        fi
    fi

    echo "ok $top" | tee "$OUT/status/$top"
}

# A worker slot: short-lived container from DEPS_IMAGE with every
# already-built wave package installed, then its chunk in sequence.
slot_run() {
    local slot=$1
    shift
    [ $# -gt 0 ] || { echo "slot $slot: no work"; return 0; }
    local ctr=${CTR}-w${slot}
    podman rm -f "$ctr" >/dev/null 2>&1 || true
    podman run -d --name "$ctr" --network=none \
        -v "$PWD/package_specs:/specs:ro,z" \
        -v "$HOME/rpmbuild/SOURCES:/sources:ro,z" \
        -v "$OUT:/out:rw,z" \
        "$DEPS_IMAGE" sleep infinity >/dev/null

    for top in $ORDER; do
        [ "$(status_of "$top")" = ok ] || continue
        podman exec "$ctr" bash -lc \
            "rpm -Uvh --nodeps --replacepkgs --replacefiles /out/build/$top/RPMS/x86_64/*.rpm && ldconfig" \
            >>"$OUT/logs/$top.log" 2>&1 || true
    done

    rc=0
    for top in "$@"; do
        build "$ctr" "$top" "$top" "$top.spec" || rc=1
    done
    podman rm -f "$ctr" >/dev/null 2>&1 || true
    echo "slot $slot done (rc=$rc)"
}

make_deps_image

LIST=${PACKAGES:-$ORDER}

# Only packages that are not yet built, FORCE handling included.
remaining=$(pending)

if [ "$WORKERS" -le 1 ]; then
    podman rm -f "$CTR" >/dev/null 2>&1 || true
    podman run -d --name "$CTR" --network=none \
        -v "$PWD/package_specs:/specs:ro,z" \
        -v "$HOME/rpmbuild/SOURCES:/sources:ro,z" \
        -v "$OUT:/out:rw,z" \
        "$DEPS_IMAGE" sleep infinity >/dev/null

    rc=0
    for top in $remaining; do
        build "$CTR" "$top" "$top" "$top.spec" || rc=1
    done
    podman commit "$CTR" "$DEPS_IMAGE" >/dev/null 2>&1 || true
    podman rm -f "$CTR" >/dev/null 2>&1 || true
else
    # round-robin the remaining packages over the slots
    declare -a chunks=()
    idx=0
    for top in $remaining; do
        chunks[$((idx++ % WORKERS))]+=" $top"
    done
    slot_pids=""
    for slot in $(seq 1 "$WORKERS"); do
        idx=$((slot-1))
        toks=(${chunks[$idx]:-})
        [ ${#toks[@]} -gt 0 ] || continue
        slot_run "$slot" "${toks[@]}" &
        slot_pids+=" $!"
    done
    [ -z "$slot_pids" ] || wait $slot_pids
fi

echo "=== summary ==="
cat "$OUT"/status/* 2>/dev/null | sort
awk '{print $1}' "$OUT"/status/* 2>/dev/null | sort | uniq -c
