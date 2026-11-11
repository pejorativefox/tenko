#!/usr/bin/env bash
# Build one spec inside a fresh, network-less build container.
#
# scripts/build/specs.sh (`tenko build`) starts one container per package
# from the build image and mounts:
#   /specs        package_specs/ (read-only)
#   /work         this package's rpmbuild topdir; SOURCES/ is pre-staged
#   /repo/local   RPMs built locally (preferred when newer)
#   /repo/cache   offline mirror of the published repository
#
# The spec's BuildRequires are installed from those two repositories, then
# rpmbuild runs.  STRICT=0 (phase 1, the default) installs whatever
# BuildRequires resolve and still builds with --nodeps against the image's
# full toolchain; STRICT=1 fails on any unresolvable BuildRequires and drops
# --nodeps, so the spec must declare everything it needs.
#
# Usage (inside the container): in_container.sh <dir>/<name>.spec
set -uo pipefail

rel=${1:?usage: in_container.sh SPEC}
spec=/specs/$rel
MAKE_JOBS=${MAKE_JOBS:-4}
STRICT=${STRICT:-0}

repos=(--disablerepo='*' --nogpgcheck
       --repofrompath=local,file:///repo/local
       --repofrompath=cache,file:///repo/cache
       --setopt=install_weak_deps=False)

defines=(--define "_topdir /work" --define "_sourcedir /work/SOURCES"
         --define "_smp_mflags -j$MAKE_JOBS"
         --define "_smp_build_ncpus $MAKE_JOBS")

echo "=== $rel (STRICT=$STRICT) in $(. /etc/os-release; echo "$PRETTY_NAME")"

if ! mapfile -t reqs < <(rpmspec -q --buildrequires "${defines[@]}" "$spec"); then
    echo "error: rpmspec could not parse $rel" >&2
    exit 1
fi
if [ ${#reqs[@]} -gt 0 ]; then
    echo "=== BuildRequires: ${reqs[*]}"
    if [ "$STRICT" = 1 ]; then
        dnf -y "${repos[@]}" install "${reqs[@]}" || {
            echo "error: BuildRequires not satisfiable (STRICT=1)" >&2; exit 1; }
    else
        # strict=0 skips names no repository provides instead of failing
        # the whole transaction; the build then relies on the image.
        dnf -y "${repos[@]}" --setopt=strict=0 install "${reqs[@]}" ||
            echo "warning: BuildRequires install failed; building with the image as is" >&2
    fi
else
    echo "=== no BuildRequires declared"
fi

# The image ships python3 without pip (built --without-ensurepip); ensurepip
# is bundled, so bootstrapping it stays offline.  Only Python packaging
# specs need it.
if grep -q 'pip' "$spec" && ! python3 -m pip --version >/dev/null 2>&1; then
    python3 -m ensurepip --upgrade >/dev/null || {
        echo "error: failed to bootstrap pip" >&2; exit 1; }
fi
# Offline, reproducible pip: no isolated build envs reaching PyPI, and
# ignore copies installed by rpm (we install into a buildroot).
export PIP_NO_BUILD_ISOLATION=1 PIP_IGNORE_INSTALLED=1
export PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_CACHE_DIR=/work/pip-cache

nodeps=(--nodeps)
[ "$STRICT" = 1 ] && nodeps=()

echo "=== rpmbuild"
mkdir -p /work/{BUILD,BUILDROOT,RPMS,SRPMS,SPECS}
rpmbuild -bb "${nodeps[@]}" "${defines[@]}" "$spec" || exit 1

# Keep failed trees for diagnosis; successful trees are just disk.
rm -rf /work/BUILD /work/BUILDROOT /work/pip-cache
