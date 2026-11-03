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
    # ISO authoring and container tooling, so an installed system can
    # rebuild the media offline.
    libburn
    libisofs
    libisoburn
    squashfs-tools
    mtools
    podman-bin
)

case "$REPO" in
    http://*|https://*|ftp://*) REPOPATH="$REPO" ;;
    *) REPOPATH="file://$REPO" ;;
esac
if [ "$REPOPATH" != "$REPO" ]; then
    [ -d "$REPO" ] || { echo "missing repo: $REPO" >&2; exit 1; }
fi

rm -rf "$OUT"
mkdir -p "$OUT"

echo "resolving the target closure from $REPO"
# dnf download is a plugin that is not installed on the build host.  Use a
# throwaway installroot with --downloadonly instead: it resolves against an
# empty rpmdb (not the host's installed set) and writes the transaction RPMs
# to $OUT.
DNFDIR=$PWD/build/dnf-iso
rm -rf "$DNFDIR"
mkdir -p "$DNFDIR"/{log,cache,persist,root}
unshare -r dnf --noplugins -y install --downloadonly \
    --destdir="$OUT" --installroot="$DNFDIR/root" \
    --setopt=reposdir=/dev/null \
    --repofrompath=browneye,"$REPOPATH" \
    --releasever=13.1 \
    --setopt=install_weak_deps=False \
    --setopt=logdir="$DNFDIR/log" \
    --setopt=cachedir="$DNFDIR/cache" \
    --setopt=persistdir="$DNFDIR/persist" \
    --nogpgcheck \
    "${PACKAGES[@]}"
rm -rf "$DNFDIR"

count=$(find "$OUT" -maxdepth 1 -name '*.rpm' | wc -l)
size=$(du -sh "$OUT" | cut -f1)
createrepo_c --quiet "$OUT"
echo "ISO repo: $count RPMs, $size at $OUT"
