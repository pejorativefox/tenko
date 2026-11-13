#!/usr/bin/env bash
# Build specs, each in a fresh network-less container from the build image.
#
# Usage:
#   tenko build curl/curl.spec libfs                # spec paths or package dirs
#   tenko build --from-file build/wave.txt          # one spec per line, # comments
#   tenko build --base                              # the whole base set (self-hosting check)
#
# Before building it makes sure that, in order:
#   1. the published repository is mirrored in build/cache/repo (`tenko sync`;
#      each RPM is downloaded once, OFFLINE=1 skips the sync),
#   2. the build image exists and is current with the mirror; it is created
#      from the mirror when missing or when the mirror has newer versions of
#      its packages (`tenko image build`),
#   3. sources are fetched once into build/sources and hard-linked into each
#      package's own SOURCES directory.
#
# Each package then gets a fresh container: BuildRequires are installed from
# build/repo (local builds) and the mirror, rpmbuild runs, and successful RPMs
# are added to build/repo so later builds can use them before they are
# published.  Builds are incremental: a package whose status says "ok" is
# skipped, so the same OUT can be reused to retry failures.  For a chain
# where one package needs another from the same run, list them in order and
# use JOBS=1.
#
# Environment:
#   OUT         output directory (default build/specs-YYYYMMDD-HHMMSS)
#   JOBS        packages built in parallel (default 4)
#   MAKE_JOBS   make -j per package (default 4)
#   STRICT      1 = build in the toolchain buildroot (BUILDROOT_IMAGE,
#               tenko-buildroot) with only the declared
#               BuildRequires added, and rpmbuild without --nodeps
#               (default 0: full build image, --nodeps; issue #58)
#   OFFLINE     1 = do not sync the mirror (it must already exist)
#   BUILD_IMAGE, BUILDROOT_IMAGE   image tags (localhost/tenko/{build,buildroot}:r6)
#
# Results: OUT/status/<pkg> (ok/fail), OUT/logs/<pkg>.log and
# OUT/build/<pkg>/RPMS; successful RPMs are also in build/repo.
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"

OUT=${OUT:-build/specs-$(date +%Y%m%d-%H%M%S)}
JOBS=${JOBS:-4}
MAKE_JOBS=${MAKE_JOBS:-4}
STRICT=${STRICT:-0}
OFFLINE=${OFFLINE:-0}

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

# 1. Offline mirror.
if [ "$OFFLINE" = 1 ]; then
    [ -f "$TENKO_REPO_CACHE/repodata/repomd.xml" ] ||
        die "OFFLINE=1 but there is no mirror in $TENKO_REPO_CACHE; run tenko sync"
else
    bash scripts/build/sync.sh
fi

# 2. Build image: the full one, or the toolchain buildroot for STRICT=1.
if [ "$STRICT" = 1 ]; then
    IMAGE=$BUILDROOT_IMAGE
    bash scripts/image/build.sh --strict
else
    IMAGE=$BUILD_IMAGE
    bash scripts/image/build.sh
fi

# 3. Local repository of our own builds.
mkdir -p "$TENKO_LOCAL_REPO"
if [ ! -f "$TENKO_LOCAL_REPO/repodata/repomd.xml" ]; then
    podman run --rm --network=none -v "$TENKO_LOCAL_REPO:/repo:rw,z" \
        "$IMAGE" createrepo_c --quiet /repo
fi

mkdir -p "$OUT"/{build,logs,status}
OUT=$(abspath "$OUT")
printf '%s\n' "${specs[@]}" >"$OUT/packages.txt"

# 4. Sources: fetched once into the shared cache, linked per package.
python3 scripts/build/fetch_sources.py --dest "$TENKO_SOURCES_DIR" \
    --stage-root "$OUT/build" "${specs[@]}"

echo "building ${#specs[@]} specs in $IMAGE -> $OUT (JOBS=$JOBS STRICT=$STRICT)"

# add_to_local_repo DIR: copy DIR's RPMs into build/repo and refresh it.
add_to_local_repo() {
    (
        flock 9
        find "$1" -name '*.rpm' -exec cp -f {} "$TENKO_LOCAL_REPO/" \;
        podman run --rm --network=none -v "$TENKO_LOCAL_REPO:/repo:rw,z" \
            "$IMAGE" createrepo_c --quiet --update /repo
    ) 9>"$TENKO_LOCAL_REPO/.lock"
}

build_one() {
    local rel=$1 pkg top start rc rpms
    pkg=$(basename "$rel" .spec)
    top=$OUT/build/$pkg
    if grep -qs '^ok ' "$OUT/status/$pkg"; then
        echo "skip $pkg (already ok)"
        return 0
    fi
    mkdir -p "$top"
    start=$(date +%s)
    podman run --rm --network=host \
        -e MAKE_JOBS="$MAKE_JOBS" -e STRICT="$STRICT" \
        -v "$PWD/package_specs:/specs:ro,z" \
        -v "$top:/work:rw,z" \
        -v "$TENKO_LOCAL_REPO:/repo/local:ro,z" \
        -v "$TENKO_REPO_CACHE:/repo/cache:ro,z" \
        -v "$PWD/scripts/build/in_container.sh:/in_container.sh:ro,z" \
        "$IMAGE" /usr/bin/bash /in_container.sh "$rel" \
        >"$OUT/logs/$pkg.log" 2>&1 && rc=0 || rc=$?
    rpms=$(find "$top/RPMS" -type f -name '*.rpm' -printf '%f ' 2>/dev/null || true)
    if [ "$rc" -eq 0 ]; then
        add_to_local_repo "$top/RPMS" >>"$OUT/logs/$pkg.log" 2>&1
        printf 'ok %s %ss %s\n' "$pkg" "$(($(date +%s) - start))" "$rpms" |
            tee "$OUT/status/$pkg"
    else
        printf 'fail %s %ss\n' "$pkg" "$(($(date +%s) - start))" |
            tee "$OUT/status/$pkg"
    fi
}

running=0
for rel in "${specs[@]}"; do
    build_one "$rel" &
    running=$((running + 1))
    if [ "$running" -ge "$JOBS" ]; then
        wait -n || true
        running=$((running - 1))
    fi
done
wait || true

echo
echo "results: $OUT"
echo "logs:    $OUT/logs"
echo "rpms:    $OUT/build/<package>/RPMS and $TENKO_LOCAL_REPO"
if grep -qs '^fail ' "$OUT"/status/*; then
    echo "failed:"
    grep -h '^fail ' "$OUT"/status/* | awk -v out="$OUT" '{print "  " $2 "  (" out "/logs/" $2 ".log)"}'
    exit 1
fi
