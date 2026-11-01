#!/usr/bin/env bash
# Shared helpers for running the repo/rootfs assembly tools from the
# self-hosted image instead of the host (E1).
#
# Source this file.  It defines:
#   TOOL_IMAGE          image that may contain dnf/createrepo_c
#   tool_image_has BIN  true if TOOL_IMAGE exists and provides BIN
#   createrepo DIR ...  run createrepo_c on DIR (image first, host fallback)
#   dnf_installrepo REPO ROOTFS [EXTRA...]
#                       install browneye-base from REPO into ROOTFS
#   rootfs_finalize ROOTFS
#                       run systemd-sysusers and systemctl preset-all offline
#   rootfs_tarball ROOTFS TARBALL
#
# TOOL_IMAGE defaults to the self-hosted base image.  That image does not
# have dnf/createrepo_c yet, so the helpers fall back to the host binaries
# until an image built with browneye-build is passed in.  Set
#   TOOL_IMAGE=localhost/browneye/base:r13.1-build-YYYYMMDD
# (see scripts/make_build_tools_image.sh) for a fully self-hosted run.

TOOL_IMAGE=${TOOL_IMAGE:-localhost/browneye/base:r13.1-selfhost-20261031}

_tool_probe=${_tool_probe:-}

tool_image_has() {
    local bin=$1
    if [ -z "$_tool_probe" ]; then
        if podman image exists "$TOOL_IMAGE" 2>/dev/null && \
           podman run --rm --network=none "$TOOL_IMAGE" \
               /usr/bin/bash -lc 'command -v dnf >/dev/null && command -v createrepo_c >/dev/null' \
               >/dev/null 2>&1; then
            _tool_probe=yes
        else
            _tool_probe=no
        fi
    fi
    [ "$_tool_probe" = yes ] || return 1
    podman run --rm --network=none "$TOOL_IMAGE" \
        /usr/bin/bash -lc "command -v $bin" >/dev/null 2>&1
}

# createrepo <directory> [extra createrepo_c args...]
createrepo() {
    local dir=$1
    shift
    dir=$(cd "$dir" && pwd)
    if tool_image_has createrepo_c; then
        echo "createrepo_c in $TOOL_IMAGE: $dir"
        podman run --rm --network=none \
            -v "$dir:/repo:rw,z" \
            "$TOOL_IMAGE" createrepo_c --quiet "$@" /repo
    else
        echo "createrepo_c (host): $dir" >&2
        createrepo_c --quiet "$@" "$dir"
    fi
}

# dnf_install_packages <repo-dir> <rootfs-dir> <package...>
dnf_install_packages() {
    local repo=$1 rootfs=$2
    shift 2
    repo=$(cd "$repo" && pwd)
    rootfs=$(cd "$(dirname "$rootfs")" && pwd)/$(basename "$rootfs")
    local parent base
    parent=$(dirname "$rootfs")
    base=$(basename "$rootfs")

    if tool_image_has dnf; then
        echo "dnf in $TOOL_IMAGE: installing $* into $rootfs"
        podman run --rm --network=none \
            -v "$repo:/repo:ro,z" \
            -v "$parent:/out:rw,z" \
            "$TOOL_IMAGE" dnf -y --nogpgcheck \
                --installroot "/out/$base" --releasever=13.1 \
                --disablerepo='*' --repofrompath=browneye,file:///repo \
                --setopt=install_weak_deps=False \
                --setopt=tsflags=noscripts \
                install "$@"
    else
        echo "dnf (host fallback): installing $* into $rootfs" >&2
        unshare -r dnf -y --nogpgcheck \
            --installroot "$rootfs" --releasever=13.1 \
            --disablerepo='*' --repofrompath=browneye,file://$repo \
            --setopt=install_weak_deps=False \
            --setopt=tsflags=noscripts \
            install "$@"
    fi
}

# dnf_installrepo <repo-dir> <rootfs-dir>
dnf_installrepo() {
    dnf_install_packages "$1" "$2" browneye-base
}

# rootfs_finalize <rootfs-dir>
rootfs_finalize() {
    local rootfs=$1
    rootfs=$(cd "$(dirname "$rootfs")" && pwd)/$(basename "$rootfs")
    if [ -x "$rootfs/usr/bin/systemd-sysusers" ]; then
        if tool_image_has dnf; then
            podman run --rm --network=none \
                -v "$rootfs:/rootfs:rw,z" \
                "$TOOL_IMAGE" chroot /rootfs /usr/bin/systemd-sysusers || true
        else
            unshare -r chroot "$rootfs" /usr/bin/systemd-sysusers || true
        fi
    fi
    if [ -x "$rootfs/usr/bin/systemctl" ]; then
        if tool_image_has dnf; then
            podman run --rm --network=none \
                -v "$rootfs:/rootfs:rw,z" \
                "$TOOL_IMAGE" chroot /rootfs /usr/bin/systemctl --root=/ preset-all || true
        else
            unshare -r chroot "$rootfs" /usr/bin/systemctl --root=/ preset-all || true
        fi
    fi
}

# rootfs_tarball <rootfs-dir> <tarball>
rootfs_tarball() {
    local rootfs=$1 tarball=$2
    rootfs=$(cd "$(dirname "$rootfs")" && pwd)/$(basename "$rootfs")
    tarball=$(cd "$(dirname "$tarball")" && pwd)/$(basename "$tarball")
    if tool_image_has dnf; then
        podman run --rm --network=none \
            -v "$rootfs:/rootfs:ro,z" \
            -v "$(dirname "$tarball"):/out:rw,z" \
            "$TOOL_IMAGE" tar -C /rootfs -czf "/out/$(basename "$tarball")" .
    else
        unshare -r tar -C "$rootfs" -czf "$tarball" .
    fi
}
