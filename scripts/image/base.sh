#!/usr/bin/env bash
# Bootstrap a Tenko build image from the published repo, on an installed
# Tenko system, without any pre-existing localhost/tenko/base image.
#
# This is the missing first step for the container workflows: it installs a
# root filesystem with dnf (rootless, via unshare -r when no tool image is
# available), finalizes it, imports it with podman, and verifies the result.
# The follow-up script then works against the image it produces:
#
#   tenko build --base
#
# Usage:
#   tenko image base
#   PACKAGES="tenko-base" IMAGE=localhost/tenko/base:r6-runtime tenko image base
#   FROM_TARBALL=build/rootfs.tar.gz IMAGE=localhost/tenko/base:imported \
#       tenko image base
#
# The tarball it writes is what `tenko publish rootfs` uploads.
#
# Environment:
#   REPO       repository to install from (default: the published Tenko repo)
#   IMAGE      image tag (default: localhost/tenko/base:r6-YYYYMMDD)
#   PACKAGES   packages to install (default: tenko-base, which carries
#              tenko-base-build and tenko-buildroot, plus DEVEL_PACKAGES)
#   DEVEL_PACKAGES  extra build-time packages: cryptsetup (libcryptsetup
#              for systemd-cryptsetup), python3-pyelftools (sd-boot) and
#              liblzo2 (btrfs-progs).  Headers and .pc files ship in the
#              runtime packages after the -devel subpackages were removed.
#   TAG_STABLE set to 0 to keep the dated tag only instead of also tagging
#              it as BASE_IMAGE
#   ROOTFS     staging rootfs directory (default: build/base-rootfs)
#   TARBALL    exported tarball (default: build/tenko-rootfs.tar.gz)
#   FROM_TARBALL  import this tarball instead of running dnf
#   TOOL_IMAGE if it provides dnf, use it for the install/finalize/tar steps
#   VERIFY_RPM package the finished image must contain (default tenko-base)
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
. scripts/lib/rootfs.sh

DATE=${DATE:-$(date +%Y%m%d)}
REPO=${REPO:-$TENKO_REPO_URL}
IMAGE=${IMAGE:-$BASE_IMAGE-$DATE}
TAG_STABLE=${TAG_STABLE:-1}
DEVEL_PACKAGES=${DEVEL_PACKAGES:-"cryptsetup python3-pyelftools liblzo2"}
PACKAGES=${PACKAGES:-tenko-base $DEVEL_PACKAGES}
ROOTFS=${ROOTFS:-build/base-rootfs}
TARBALL=${TARBALL:-build/tenko-rootfs.tar.gz}
FROM_TARBALL=${FROM_TARBALL:-}

mkdir -p "$(dirname "$ROOTFS")" "$(dirname "$TARBALL")"
rootfs_abs=$(abspath "$ROOTFS")
tarball_abs=$(abspath "$TARBALL")

if [ -n "$FROM_TARBALL" ]; then
    [ -f "$FROM_TARBALL" ] || { echo "missing tarball: $FROM_TARBALL" >&2; exit 1; }
    tarball_abs=$(abspath "$FROM_TARBALL")
    echo "importing $tarball_abs"
else
    rm -rf "$rootfs_abs" "$tarball_abs"
    mkdir -p "$rootfs_abs"

    # tenko-basefs owns the /bin, /sbin, /lib and /lib64 usr-merge symlinks.
    # Install it in its own transaction first: if the packages that create
    # those directories land in the same transaction, rpm fails with
    # "File from package already exists as a directory in system".
    dnf_install "$REPO" "$rootfs_abs" tenko-basefs

    # shellcheck disable=SC2086  # PACKAGES is a word list
    dnf_install "$REPO" "$rootfs_abs" $PACKAGES

    # dnf --installroot writes the RPM database to the host's %_dbpath.  The
    # image keeps it in /usr/lib/sysimage/rpm (/var/lib/rpm is a symlink), so
    # move a database that landed in a real /var/lib/rpm.
    if [ -d "$rootfs_abs/var/lib/rpm" ] && [ ! -L "$rootfs_abs/var/lib/rpm" ] && \
       [ ! -d "$rootfs_abs/usr/lib/sysimage/rpm" ]; then
        echo "relocating the RPM database to /usr/lib/sysimage/rpm"
        mkdir -p "$rootfs_abs/usr/lib/sysimage/rpm"
        find "$rootfs_abs/var/lib/rpm" -mindepth 1 -maxdepth 1 \
            -exec mv {} "$rootfs_abs/usr/lib/sysimage/rpm/" \;
        rmdir "$rootfs_abs/var/lib/rpm"
    fi
    # rpm in the image reads %_dbpath /var/lib/rpm; point it at the database.
    if [ -d "$rootfs_abs/usr/lib/sysimage/rpm" ] && [ ! -e "$rootfs_abs/var/lib/rpm" ]; then
        mkdir -p "$rootfs_abs/var/lib"
        ln -s /usr/lib/sysimage/rpm "$rootfs_abs/var/lib/rpm"
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
podman run --rm --network=none -e VERIFY_RPM="${VERIFY_RPM:-tenko-base}" "$IMAGE" /usr/bin/bash -lc '
    set -e
    echo "packages: $(rpm -qa | wc -l)"
    rpm -q $VERIFY_RPM
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

if [ "$TAG_STABLE" = 1 ] && [ "$IMAGE" != "$BASE_IMAGE" ]; then
    podman tag "$IMAGE" "$BASE_IMAGE"
    echo "tagged $BASE_IMAGE"
fi

echo "created $IMAGE"
[ -n "${NO_NEXT_HINT:-}" ] || echo "next: BASE_IMAGE=$IMAGE tenko build --base"
