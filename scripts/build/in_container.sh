#!/usr/bin/env bash
# Build one spec inside a fresh build container (host network).
#
# scripts/build/specs.sh (`tenko build`) starts one container per package
# from the build image and mounts:
#   /specs        package_specs/ (read-only)
#   /work         this package's rpmbuild topdir; SOURCES/ is pre-staged
#   /repo/local   RPMs built locally (preferred when newer)
#   /repo/cache   mirror of the published repository (tenko sync)
#
# The spec's BuildRequires are installed from those two repositories,
# followed by their pkg-config closure (tenko-builddep, run from /specs so the
# image needs no rebuild when it changes), then rpmbuild runs without
# --nodeps.  An unresolvable BuildRequires fails the build: the image holds
# only tenko-buildroot, so the spec must declare everything it needs.
#
# Usage (inside the container): in_container.sh <dir>/<name>.spec
set -uo pipefail

rel=${1:?usage: in_container.sh SPEC}
spec=/specs/$rel
MAKE_JOBS=${MAKE_JOBS:-4}

repos=(--disablerepo='*' --nogpgcheck
       --repofrompath=local,file:///repo/local
       --repofrompath=cache,file:///repo/cache
       --setopt=install_weak_deps=False)

defines=(--define "_topdir /work" --define "_sourcedir /work/SOURCES"
         --define "_smp_mflags -j$MAKE_JOBS"
         --define "_smp_build_ncpus $MAKE_JOBS")

echo "=== $rel in $(rpm -q --qf "%{name}-%{version}-%{release}" tenko-buildroot tenko-base 2>/dev/null | grep -v "not installed" | head -1)"

if ! mapfile -t reqs < <(rpmspec -q --buildrequires "${defines[@]}" "$spec"); then
    echo "error: rpmspec could not parse $rel" >&2
    exit 1
fi
if [ ${#reqs[@]} -gt 0 ]; then
    echo "=== BuildRequires: ${reqs[*]}"
    dnf -y "${repos[@]}" install "${reqs[@]}" || {
        echo "error: BuildRequires not satisfiable" >&2; exit 1; }
    # .pc Requires are not RPM requirements here (macros.tenko): install the
    # packages the declared libraries' .pc files name.
    bash /specs/tenko-rpm-config/files/tenko-builddep "${repos[@]}" -- "${reqs[@]}"
else
    echo "=== no BuildRequires declared"
fi

# The image ships python3 without pip (built --without-ensurepip); only
# Python packaging specs need it, so bootstrap it from the bundled ensurepip.
if grep -q 'pip' "$spec" && ! python3 -m pip --version >/dev/null 2>&1; then
    python3 -m ensurepip --upgrade >/dev/null || {
        echo "error: failed to bootstrap pip" >&2; exit 1; }
fi
# Build Python packages against the packaged build backends (no isolated
# build envs pulled from PyPI), and ignore copies installed by rpm (we
# install into a buildroot).
export PIP_NO_BUILD_ISOLATION=1 PIP_IGNORE_INSTALLED=1
export PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_CACHE_DIR=/work/pip-cache

echo "=== rpmbuild"
mkdir -p /work/{BUILD,BUILDROOT,RPMS,SRPMS,SPECS}
rpmbuild -bb "${defines[@]}" "$spec" || exit 1

# Keep failed trees for diagnosis; successful trees are just disk.
rm -rf /work/BUILD /work/BUILDROOT /work/pip-cache
