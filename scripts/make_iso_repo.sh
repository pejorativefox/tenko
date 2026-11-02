#!/usr/bin/env bash
# Build the pruned package repository that goes on the installer ISO.
#
# The closure is exactly what the installer can install: the base system, the
# XFCE desktop (which pulls lightdm/accountsservice/sudo/librsvg) and the boot
# tooling.  Keep this list in sync with browneye-installer's target set.
set -euo pipefail
cd "$(dirname "$0")/.."

REPO=${REPO:-$PWD/build/repo-all}
OUT=${OUT:-$PWD/build/iso-repo}

PACKAGES=(
    browneye-base
    xfce-desktop
    linux-kernel
    linux-modules
    grub
    dracut
    efibootmgr
    dosfstools
    dnf
    sudo
    opencode-bin
    herdr
    browneye-build
)

[ -d "$REPO" ] || { echo "missing repo: $REPO" >&2; exit 1; }

rm -rf "$OUT"
mkdir -p "$OUT"

echo "resolving the target closure from $REPO"
dnf --refresh \
    --setopt=reposdir=/dev/null \
    --repofrompath=browneye,file://$REPO \
    --releasever=13.1 \
    --setopt=install_weak_deps=False \
    --nogpgcheck \
    download --resolve --alldeps --destdir="$OUT" "${PACKAGES[@]}"

count=$(find "$OUT" -maxdepth 1 -name '*.rpm' | wc -l)
size=$(du -sh "$OUT" | cut -f1)
createrepo_c --quiet "$OUT"
echo "ISO repo: $count RPMs, $size at $OUT"
