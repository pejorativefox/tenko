# Rootfs and repository helpers.  Source after lib/common.sh.
#
#   createrepo DIR [ARGS...]          createrepo_c over DIR
#   dnf_install REPO ROOTFS PKG...    install packages into ROOTFS from REPO
#                                     (a directory or URL), scriptlets off
#   rootfs_finalize ROOTFS            systemd-sysusers + systemctl preset-all
#   rootfs_tarball ROOTFS TARBALL     gzip tarball of ROOTFS
#
# Each helper runs its tool inside TOOL_IMAGE when that image provides dnf
# and createrepo_c, and on the host (rootless, via unshare -r) otherwise.
# TOOL_IMAGE defaults to BASE_IMAGE.

TOOL_IMAGE=${TOOL_IMAGE:-$BASE_IMAGE}
_tool_probe=

# use_tool_image: true when TOOL_IMAGE exists and has dnf and createrepo_c.
use_tool_image() {
    if [ -z "$_tool_probe" ]; then
        if podman image exists "$TOOL_IMAGE" 2>/dev/null &&
           podman run --rm --network=none "$TOOL_IMAGE" /usr/bin/bash -c \
               'command -v dnf && command -v createrepo_c' >/dev/null 2>&1; then
            _tool_probe=yes
        else
            _tool_probe=no
            echo "note: $TOOL_IMAGE has no dnf/createrepo_c; using host tools" >&2
        fi
    fi
    [ "$_tool_probe" = yes ]
}

createrepo() {
    local dir
    dir=$(cd "$1" && pwd)
    shift
    if use_tool_image; then
        podman run --rm --network=none -v "$dir:/repo:rw,z" \
            "$TOOL_IMAGE" createrepo_c --quiet "$@" /repo
    else
        createrepo_c --quiet "$@" "$dir"
    fi
}

dnf_install() {
    local repo rootfs parent base net=none
    repo=$(repo_url "$1")
    rootfs=$(abspath "$2")
    shift 2
    parent=$(dirname "$rootfs")
    base=$(basename "$rootfs")
    mkdir -p "$rootfs"

    local dnf_args=(-y --nogpgcheck --releasever="$TENKO_RELEASE"
        --disablerepo='*' --setopt=install_weak_deps=False
        --setopt=tsflags=noscripts)
    echo "installing $* into $rootfs from $repo"
    if use_tool_image; then
        local mounts=(-v "$parent:/out:rw,z")
        case "$repo" in
            file://*) mounts+=(-v "${repo#file://}:/repo:ro,z"); repo=file:///repo ;;
            *) net=host ;;
        esac
        podman run --rm --network="$net" "${mounts[@]}" "$TOOL_IMAGE" \
            dnf "${dnf_args[@]}" --installroot "/out/$base" \
                --repofrompath=tenko,"$repo" install "$@"
    else
        unshare -r dnf "${dnf_args[@]}" --installroot "$rootfs" \
            --repofrompath=tenko,"$repo" install "$@"
    fi
}

# _in_rootfs ROOTFS CMD...: run CMD chrooted into ROOTFS.
_in_rootfs() {
    local rootfs
    rootfs=$(abspath "$1")
    shift
    if use_tool_image; then
        podman run --rm --network=none -v "$rootfs:/rootfs:rw,z" \
            "$TOOL_IMAGE" chroot /rootfs "$@"
    else
        unshare -r chroot "$rootfs" "$@"
    fi
}

rootfs_finalize() {
    if [ -x "$1/usr/bin/systemd-sysusers" ]; then
        _in_rootfs "$1" /usr/bin/systemd-sysusers || true
    fi
    if [ -x "$1/usr/bin/systemctl" ]; then
        _in_rootfs "$1" /usr/bin/systemctl --root=/ preset-all || true
    fi
}

rootfs_tarball() {
    local rootfs tarball
    rootfs=$(abspath "$1")
    tarball=$(abspath "$2")
    if use_tool_image; then
        podman run --rm --network=none \
            -v "$rootfs:/rootfs:ro,z" -v "$(dirname "$tarball"):/out:rw,z" \
            "$TOOL_IMAGE" tar -C /rootfs -czf "/out/$(basename "$tarball")" .
    else
        unshare -r tar -C "$rootfs" -czf "$tarball" .
    fi
}
