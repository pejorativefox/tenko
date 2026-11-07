#!/usr/bin/env bash
# Build an arbitrary list of specs in a Tenko container image.
#
# Unlike verify_base_in_container.sh (which rebuilds ORDER), this is the
# general driver for one-off waves: D7 spec bumps, single packages, etc.
#
# Usage:
#   IMAGE=localhost/tenko/base:d7 OUT=build/d7/out \
#       scripts/build_specs.sh libfs/libfs.spec libxvmc/libxvmc.spec
#   IMAGE=... OUT=... scripts/build_specs.sh --from-file build/d7/pkglist.txt
#
# Paths are relative to package_specs/.  Builds are incremental: a package
# whose status file says "ok" is skipped, so the same OUT can be re-used to
# retry failures.
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/repo_tools.sh

usage() { sed -n '2,17p' "$0"; exit "${1:-0}"; }

IMAGE=${IMAGE:-$(pick_image localhost/tenko/base:r13.1)}
OUT=${OUT:-build/specs-$(date +%Y%m%d-%H%M%S)}
JOBS=${JOBS:-4}
MAKE_JOBS=${MAKE_JOBS:-4}

specs=()
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help) usage 0 ;;
        --from-file)
            while IFS= read -r line; do
                line=${line%%#*}
                line=$(echo "$line" | tr -d '[:space:]')
                [ -n "$line" ] && specs+=("$line")
            done <"$2"
            shift 2
            ;;
        *) specs+=("$1"); shift ;;
    esac
done

if [ ${#specs[@]} -eq 0 ]; then
    echo "no specs given" >&2
    usage 2
fi

for rel in "${specs[@]}"; do
    [ -f "package_specs/$rel" ] || { echo "missing spec: package_specs/$rel" >&2; exit 2; }
done

mkdir -p "$OUT"
printf '%s\n' "${specs[@]}" >"$OUT/packages.txt"
echo "building ${#specs[@]} specs in $IMAGE -> $OUT"

# rpmbuild reads %{_sourcedir}; stage the per-spec helper files (patches,
# unit files, macros, static %files lists) next to the tarballs.
staged=0
for f in package_specs/*/files/*; do
    [ -f "$f" ] || continue
    cp -f "$f" "$HOME/rpmbuild/SOURCES/"
    staged=$((staged + 1))
done
echo "staged $staged spec-side files into $HOME/rpmbuild/SOURCES"

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
