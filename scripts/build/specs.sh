#!/usr/bin/env bash
# Build specs with rpmbuild inside the base container (no network).
#
# Usage:
#   tenko build curl/curl.spec libfs                # spec paths or package dirs
#   tenko build --from-file build/wave.txt          # one spec per line, # comments
#   tenko build --base                              # the whole base set (self-hosting check)
#
# Sources listed in package_specs/<pkg>/sources are fetched and md5-verified
# into ~/rpmbuild/SOURCES first, together with each package's files/.  Builds
# are incremental: a package whose status file says "ok" is skipped, so the
# same OUT can be reused to retry failures.
#
# Environment:
#   BASE_IMAGE  build image (default localhost/tenko/base:r6; `tenko image base`)
#   OUT         output directory (default build/specs-YYYYMMDD-HHMMSS)
#   JOBS        packages built in parallel (default 4)
#   MAKE_JOBS   make -j per package (default 4)
#
# Results: OUT/status/<pkg> (ok/fail), OUT/logs/<pkg>.log and
# OUT/build/<pkg>/RPMS.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"

OUT=${OUT:-build/specs-$(date +%Y%m%d-%H%M%S)}
JOBS=${JOBS:-4}
MAKE_JOBS=${MAKE_JOBS:-4}
SOURCES=$HOME/rpmbuild/SOURCES

# spec_for NAME-OR-PATH: the spec path relative to package_specs/.
spec_for() {
    local arg=${1#package_specs/}
    case "$arg" in
        *.spec) [ -f "package_specs/$arg" ] && { echo "$arg"; return; } ;;
        *) arg=${arg%/}
           [ -f "package_specs/$arg/$arg.spec" ] && { echo "$arg/$arg.spec"; return; } ;;
    esac
    die "missing spec: $1"
}

# The base set, in build_order, plus the glue tenko-base pulls in.
base_specs() {
    python3 - <<'PY'
import glob, json, os, sys
with open("package_specs/base.json", encoding="utf-8") as handle:
    base = json.load(handle)
aliases = base.get("aliases", {})
names = list(base.get("build_order", []))
names += ["libbsd", "libmd", "libseccomp", "libunistring", "libtasn1",
          "p11-kit", "make-ca", "tenko-base"]
seen = set()
for name in names:
    directory = aliases.get(name, name)
    if directory in seen:
        continue
    seen.add(directory)
    canonical = os.path.join("package_specs", directory, directory + ".spec")
    specs = [canonical] if os.path.isfile(canonical) else sorted(
        glob.glob(os.path.join("package_specs", directory, "*.spec")))
    if not specs:
        print("warning: no spec for {} ({})".format(name, directory), file=sys.stderr)
    for spec in specs:
        print(os.path.relpath(spec, "package_specs"))
PY
}

specs=()
while [ $# -gt 0 ]; do
    case "$1" in
        --base) mapfile -t -O "${#specs[@]}" specs < <(base_specs); shift ;;
        --from-file)
            [ -f "${2:-}" ] || die "missing list: ${2:-}"
            while IFS= read -r line; do
                line=${line%%#*}
                line=$(echo "$line" | tr -d '[:space:]')
                [ -n "$line" ] && specs+=("$(spec_for "$line")")
            done <"$2"
            shift 2
            ;;
        -*) die "unknown option: $1 (see tenko build --help)" ;;
        *) specs+=("$(spec_for "$1")"); shift ;;
    esac
done
[ ${#specs[@]} -gt 0 ] || die "no specs given (see tenko build --help)"

mkdir -p "$OUT" "$SOURCES"
OUT=$(abspath "$OUT")
printf '%s\n' "${specs[@]}" >"$OUT/packages.txt"
echo "building ${#specs[@]} specs in $BASE_IMAGE -> $OUT"

# rpmbuild reads %{_sourcedir}; stage the per-spec helper files (patches,
# unit files, macros, static %files lists) next to the tarballs.
staged=0
for f in package_specs/*/files/*; do
    [ -f "$f" ] || continue
    cp -f "$f" "$SOURCES/"
    staged=$((staged + 1))
done
echo "staged $staged spec-side files into $SOURCES"

python3 scripts/build/fetch_sources.py --dest "$SOURCES" "${specs[@]}"

podman run --rm --network=none \
    -e JOBS="$JOBS" -e MAKE_JOBS="$MAKE_JOBS" \
    -v "$PWD/package_specs:/specs:ro,z" \
    -v "$SOURCES:/sources:ro,z" \
    -v "$PWD/scripts/build/in_container.sh:/in_container.sh:ro,z" \
    -v "$OUT:/out:rw,z" \
    "$BASE_IMAGE" /usr/bin/bash /in_container.sh

echo
echo "results: $OUT"
echo "logs:    $OUT/logs"
echo "rpms:    $OUT/build/<package>/RPMS"
if grep -qs '^fail ' "$OUT"/status/*; then
    echo "failed:"
    grep -h '^fail ' "$OUT"/status/* | awk -v out="$OUT" '{print "  " $2 "  (" out "/logs/" $2 ".log)"}'
    exit 1
fi
