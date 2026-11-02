#!/usr/bin/env bash
# Bootstrap a Browneye build image from the published repo, on an installed
# Browneye system, without any pre-existing localhost/browneye/base image.
#
# This is the missing first step for the container workflows: it installs a
# root filesystem with dnf (rootless, via unshare -r when no tool image is
# available), finalizes it, imports it with podman, and verifies the result.
# The two follow-up scripts then work against the image it produces:
#
#   IMAGE=<image> OUT=build/container-rebuild scripts/verify_base_in_container.sh
#   TOOL_IMAGE=<image> scripts/make_build_tools_image.sh
#
# Usage:
#   scripts/make_base_image.sh
#   PACKAGES="browneye-base" IMAGE=localhost/browneye/base:r13.1-runtime \
#       scripts/make_base_image.sh
#   FROM_TARBALL=build/rootfs.tar.gz IMAGE=localhost/browneye/base:imported \
#       scripts/make_base_image.sh
#
# Environment:
#   REPO_URL   published repo (default: the Browneye 13.1 repo)
#   IMAGE      image tag (default: localhost/browneye/base:r13.1-YYYYMMDD)
#   PACKAGES   packages to install (default: browneye-base browneye-build
#              plus DEVEL_PACKAGES)
#   DEVEL_PACKAGES  header packages needed to rebuild the base set inside the
#              image (default: ncurses/readline/xz/pam/elfutils/perl/tcl/
#              e2fsprogs/kmod -devel)
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
REPO_URL=${REPO_URL:-https://tomfool.8bit.ca/browneye/packages/13.1/}
IMAGE=${IMAGE:-localhost/browneye/base:r13.1-$DATE}
TAG_STABLE=${TAG_STABLE:-1}
DEVEL_PACKAGES=${DEVEL_PACKAGES:-ncurses-devel readline-devel xz-devel \
    linux-pam-devel elfutils-devel perl-devel tcl-devel e2fsprogs-devel \
    kmod-devel expat-devel sqlite-devel util-linux-devel pcre2-devel}
PACKAGES=${PACKAGES:-browneye-base browneye-build $DEVEL_PACKAGES}
ROOTFS=${ROOTFS:-build/base-rootfs}
TARBALL=${TARBALL:-build/base-rootfs.tar.gz}
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
                --installroot "/out/$(basename "$rootfs_abs")" --releasever=13.1 \
                --disablerepo='*' --repofrompath=browneye,"$REPO_URL" \
                --setopt=install_weak_deps=False \
                --setopt=tsflags=noscripts \
                install $PACKAGES
    else
        echo "dnf (host, rootless): no image with dnf; using unshare -r" >&2
        unshare -r dnf -y --nogpgcheck \
            --installroot "$rootfs_abs" --releasever=13.1 \
            --disablerepo='*' --repofrompath=browneye,"$REPO_URL" \
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
    rpm -q browneye-base
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

if [ "$TAG_STABLE" = 1 ] && [ "$IMAGE" != "localhost/browneye/base:r13.1" ]; then
    podman tag "$IMAGE" localhost/browneye/base:r13.1
    echo "tagged localhost/browneye/base:r13.1 (stable name used by the scripts)"
fi

echo "created $IMAGE"
echo "next: IMAGE=$IMAGE OUT=build/container-rebuild scripts/verify_base_in_container.sh"
echo "next: TOOL_IMAGE=$IMAGE scripts/make_build_tools_image.sh   # dnf/createrepo_c image"
