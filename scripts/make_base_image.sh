#!/usr/bin/env bash
# Bootstrap a Tenko build image from the published repo, on an installed
# Tenko system, without any pre-existing localhost/tenko/base image.
#
# This is the missing first step for the container workflows: it installs a
# root filesystem with dnf (rootless, via unshare -r when no tool image is
# available), finalizes it, imports it with podman, and verifies the result.
# The follow-up script then works against the image it produces:
#
#   IMAGE=<image> OUT=build/container-rebuild scripts/verify_base_in_container.sh
#
# Usage:
#   scripts/make_base_image.sh
#   PACKAGES="tenko-base" IMAGE=localhost/tenko/base:r13.1-runtime \
#       scripts/make_base_image.sh
#   FROM_TARBALL=build/rootfs.tar.gz IMAGE=localhost/tenko/base:imported \
#       scripts/make_base_image.sh
#
# Environment:
#   REPO_URL   published repo (default: the Tenko 6 repo)
#   IMAGE      image tag (default: localhost/tenko/base:r13.1-YYYYMMDD)
#   PACKAGES   packages to install (default: tenko-base tenko-build
#              plus DEVEL_PACKAGES)
#   DEVEL_PACKAGES  extra build-time packages.  Headers and .pc files ship
#              in the runtime packages after the -devel subpackages were
#              removed, so only python3-pyelftools is needed (systemd
#              requires it for -D bootloader=enabled)
#   TAG_STABLE set to 0 to keep the dated tag only (e.g. for a lean E2 image
#              that must not replace the dnf-capable base:r13.1)
#   ROOTFS     staging rootfs directory (default: build/base-rootfs)
#   TARBALL    exported tarball (default: build/base-rootfs.tar.gz)
#   FROM_TARBALL  import this tarball instead of running dnf
#   TOOL_IMAGE if it provides dnf, use it for the install/finalize/tar steps
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/repo_tools.sh

DATE=${DATE:-$(date +%Y%m%d)}
REPO_URL=${REPO_URL:-https://repo.pjfox.xyz/tenko/packages/6/}
IMAGE=${IMAGE:-localhost/tenko/base:r13.1-$DATE}
TAG_STABLE=${TAG_STABLE:-1}
DEVEL_PACKAGES=${DEVEL_PACKAGES:-"python3-pyelftools liblzo2"}
PACKAGES=${PACKAGES:-tenko-base tenko-build $DEVEL_PACKAGES}
ROOTFS=${ROOTFS:-build/base-rootfs}
TARBALL=${TARBALL:-build/tenko-rootfs.tar.gz}
FROM_TARBALL=${FROM_TARBALL:-}

case "${1:-}" in
    -h|--help) sed -n '2,35p' "$0"; exit 0 ;;
    "") ;;
    *) echo "usage: $0 [--help]" >&2; exit 2 ;;
esac

rootfs_abs=$(cd "$(dirname "$ROOTFS")" && pwd)/$(basename "$ROOTFS")
tarball_abs=$(cd "$(dirname "$TARBALL")" && pwd)/$(basename "$TARBALL")
mkdir -p "$(dirname "$rootfs_abs")" "$(dirname "$tarball_abs")"

if [ -n "$FROM_TARBALL" ]; then
    [ -f "$FROM_TARBALL" ] || { echo "missing tarball: $FROM_TARBALL" >&2; exit 1; }
    tarball_abs=$(cd "$(dirname "$FROM_TARBALL")" && pwd)/$(basename "$FROM_TARBALL")
    echo "importing $tarball_abs"
else
    rm -rf "$rootfs_abs" "$tarball_abs"
    mkdir -p "$rootfs_abs"

    echo "installing $PACKAGES into $rootfs_abs from $REPO_URL"
    if tool_image_has dnf; then
        podman run --rm --network=host \
            -v "$(dirname "$rootfs_abs"):/out:rw,z" \
            "$TOOL_IMAGE" dnf -y --nogpgcheck \
                --installroot "/out/$(basename "$rootfs_abs")" --releasever=6 \
                --disablerepo='*' --repofrompath=tenko,"$REPO_URL" \
                --setopt=install_weak_deps=False \
                --setopt=tsflags=noscripts \
                install $PACKAGES
    else
        echo "dnf (host, rootless): no image with dnf; using unshare -r" >&2
        unshare -r dnf -y --nogpgcheck \
            --installroot "$rootfs_abs" --releasever=6 \
            --disablerepo='*' --repofrompath=tenko,"$REPO_URL" \
            --setopt=install_weak_deps=False \
            --setopt=tsflags=noscripts \
            install $PACKAGES
    fi

    # The install ran with tsflags=noscripts, so run the offline setup that
    # matters for a working image: sysusers and systemd presets.
    rootfs_finalize "$rootfs_abs"

    # Podman supplies /dev, /proc, /sys and /etc/resolv.conf at runtime; the
    # empty mount points and a writable /tmp keep tools that expect them happy.
    mkdir -p "$rootfs_abs"/proc "$rootfs_abs"/sys "$rootfs_abs"/dev \
             "$rootfs_abs"/run "$rootfs_abs"/tmp
    chmod 1777 "$rootfs_abs/tmp"
    if [ ! -e "$rootfs_abs/etc/machine-id" ]; then
        : > "$rootfs_abs/etc/machine-id"
    fi

    rootfs_tarball "$rootfs_abs" "$tarball_abs"
fi

echo "building $IMAGE from $tarball_abs"
# podman only accepts build-context-relative ADD sources, so use the
# tarball's directory as the context.
build_ctx=$(dirname "$tarball_abs")
tar_name=$(basename "$tarball_abs")
(cd "$build_ctx" && podman build -t "$IMAGE" -f - . <<EOF
FROM scratch
ADD ${tar_name} /
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV LANG=C.UTF-8
ENV container=podman
WORKDIR /build
CMD ["/bin/bash"]
EOF
)

echo "verifying $IMAGE"
podman run --rm "$IMAGE" /usr/bin/bash -lc '
    set -e
    echo "packages: $(rpm -qa | wc -l)"
    rpm -q tenko-base
    for bin in gcc rpmbuild make python3 meson perl; do
        printf "%-9s " "$bin"
        command -v "$bin" || { echo missing; exit 1; }
    done
    gcc --version | head -1
    python3 --version
    rpmbuild --version
    if command -v dnf >/dev/null; then
        dnf --version | head -1
        createrepo_c --version | head -1
    fi
'

if [ "$TAG_STABLE" = 1 ] && [ "$IMAGE" != "localhost/tenko/base:r13.1" ]; then
    podman tag "$IMAGE" localhost/tenko/base:r13.1
    # Keep the pre-rename tag until checkpoint 7 rebuilds the image.
    podman tag "$IMAGE" localhost/browneye/base:r13.1
    echo "tagged localhost/tenko/base:r13.1 (old browneye tag kept as alias)"
fi

echo "created $IMAGE"
echo "next: IMAGE=$IMAGE OUT=build/container-rebuild scripts/verify_base_in_container.sh"
