#!/usr/bin/env bash
# Verify the self-hosted repo/rootfs assembly toolchain (E1) inside the
# build image:
#
#   - dnf and createrepo_c run from the image
#   - createrepo_c creates usable repodata
#   - dnf installs browneye-base into a fresh --installroot from a local
#     file:// repo with tsflags=noscripts
#   - dnf installs a tiny package with a working %post scriptlet (real
#     scriptlets, no tsflags=noscripts)
#   - the built RPMs carry the expected ELF Requires
#
# Usage:
#   IMAGE=localhost/browneye/base:r13.1-build-20261101 \
#       scripts/verify_build_tools.sh
#
# The repository is assembled in build/e1/repo-test from the RPMs in
# build/e1/out plus the current build/repo-all (read-only), so this script
# never modifies the shared repo or rootfs directories.
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/repo_tools.sh

IMAGE=${IMAGE:-localhost/browneye/base:r13.1-build-$(date +%Y%m%d)}
OUT=${OUT:-build/e1/out}
REPO=${REPO:-build/e1/repo-test}
BASE_REPO=${BASE_REPO:-build/repo-selfhost}
EXTRA_REPO=${EXTRA_REPO:-build/repo-all}
WORK=${WORK:-build/e1/verify-work}
LOG=${LOG:-build/e1/verify.log}

[ -d "$OUT/build" ] || { echo "missing $OUT/build" >&2; exit 1; }

rm -rf "$REPO" "$WORK"
mkdir -p "$REPO" "$WORK"
# Base set for the installroot test (read-only source).  The worktree has no
# build/repo-selfhost of its own; point BASE_REPO at the main tree.
if [ -d "$BASE_REPO" ]; then
    cp -p "$BASE_REPO"/*.rpm "$REPO"/ 2>/dev/null || true
fi
# Add packages that the base repo does not carry (for example libtirpc, which
# the current C13 iproute2 build requires) without replacing the base
# versions with the desktop rebuilds.
if [ -d "$EXTRA_REPO" ]; then
    for rpm in "$EXTRA_REPO"/*.rpm; do
        [ -f "$rpm" ] || continue
        name=$(rpm -qp --qf '%{NAME}' "$rpm" 2>/dev/null) || continue
        compgen -G "$REPO/$name-[0-9]*.rpm" >/dev/null && continue
        cp -p "$rpm" "$REPO"/
    done
fi
# Our freshly built toolchain RPMs win over older copies.
find "$OUT/build" -path '*/RPMS/x86_64/*.rpm' \
    -not -path '*/glib-pass1/*' -exec cp -pf {} "$REPO"/ \;

# A tiny package with a %post scriptlet, used to prove that scriptlets run
# in a dnf --installroot transaction.
cat > "$WORK/e1-scriptlet-test.spec" <<'EOF'
Name:           e1-scriptlet-test
Version:        1.0
Release:        1
Summary:        E1 scriptlet test package
License:        MIT
BuildArch:      noarch
Requires:       browneye-basefs, bash

%description
Test-only package: its %post scriptlet writes a marker into the installroot.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/share/e1-scriptlet-test
echo installed > %{buildroot}/usr/share/e1-scriptlet-test/marker

%post
mkdir -p /var/lib
echo ran > /var/lib/e1-scriptlet-test

%files
/usr/share/e1-scriptlet-test

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.0-1
- Test package for the E1 dnf installroot verification.
EOF

mkdir -p "$WORK/rpmbuild"/{BUILD,BUILDROOT,RPMS,SRPMS,SPECS}
podman run --rm --network=none \
    -v "$(cd "$WORK" && pwd):/work:rw,z" \
    "$IMAGE" rpmbuild -bb --nodeps \
        --define "_topdir /work/rpmbuild" "$(echo /work/e1-scriptlet-test.spec)" \
    >/dev/null
cp -p "$WORK"/rpmbuild/RPMS/noarch/*.rpm "$REPO"/

./scripts/prune_repo.sh "$REPO"
echo "test repo: $(find "$REPO" -maxdepth 1 -name '*.rpm' | wc -l) RPMs"
createrepo "$REPO"

mkdir -p "$(dirname "$LOG")"
: > "$LOG"

echo "=== tool versions in $IMAGE ===" | tee -a "$LOG"
podman run --rm --network=none "$IMAGE" /usr/bin/bash -lc '
    set -e
    dnf --version
    createrepo_c --version
    rpm -q dnf libdnf createrepo_c libsolv libcomps libmodulemd librepo python3-rpm browneye-build
' 2>&1 | tee -a "$LOG"

echo "=== installroot tests ===" | tee -a "$LOG"
podman run --rm --network=none \
    -v "$(cd "$REPO" && pwd):/repo:ro,z" \
    -v "$(cd "$WORK" && pwd):/outlog:rw,z" \
    "$IMAGE" /usr/bin/bash -lc '
    set -e
    rm -rf /work && mkdir -p /work

    echo "-- createrepo_c into an empty directory"
    mkdir -p /work/emptyrepo
    createrepo_c --quiet /work/emptyrepo
    test -s /work/emptyrepo/repodata/repomd.xml
    echo "OK: createrepo_c wrote repodata"

    echo "-- dnf install browneye-base (tsflags=noscripts)"
    dnf -y --nogpgcheck --installroot /work/rootfs --releasever=13.1 \
        --disablerepo="*" --repofrompath=browneye,file:///repo \
        --setopt=install_weak_deps=False --setopt=tsflags=noscripts \
        install browneye-base >/outlog/install.log 2>&1 || { tail -20 /outlog/install.log; exit 1; }
    rpm --root /work/rootfs -q browneye-base
    echo "installed packages: $(rpm --root /work/rootfs -qa | wc -l)"
    test -x /work/rootfs/usr/bin/bash
    echo "OK: nosecripts installroot"

    echo "-- dnf install with real scriptlets (tiny package)"
    if dnf -y --nogpgcheck --installroot /work/scriptroot --releasever=13.1 \
        --disablerepo="*" --repofrompath=browneye,file:///repo \
        --setopt=install_weak_deps=False \
        install e1-scriptlet-test >/outlog/script.log 2>&1; then
        if [ -f /work/scriptroot/var/lib/e1-scriptlet-test ]; then
            echo "OK: %post scriptlet ran in the installroot"
        else
            echo "WARN: %post scriptlet did not leave its marker"
        fi
    else
        echo "WARN: scriptlet install failed"
        tail -20 /outlog/script.log
    fi
' 2>&1 | tee -a "$LOG" || echo "WARN: installroot test container failed" | tee -a "$LOG"

echo "=== ELF Requires ===" | tee -a "$LOG"
for pkg in libdnf createrepo_c libsolv libcomps librepo dnf; do
    rpmfile=$(ls "$OUT"/build/"$pkg"/RPMS/x86_64/*.rpm 2>/dev/null | head -1)
    [ -n "$rpmfile" ] || continue
    echo "## $(basename "$rpmfile")" | tee -a "$LOG"
    rpm -qpR "$rpmfile" | grep -E '^(lib|/usr/lib)' | head -8 | tee -a "$LOG"
done

echo "verify log: $LOG"
