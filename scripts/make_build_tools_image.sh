#!/usr/bin/env bash
# Build the self-hosted build image: browneye-base plus the browneye-build
# toolchain (dnf, createrepo_c and their dependencies) so the image can
# build RPMs *and* assemble repos and root filesystems without host tools.
#
# Usage:
#   scripts/make_build_tools_image.sh
#   BASE_IMAGE=localhost/browneye/base:r13.1-selfhost-20261101 \
#   IMAGE=localhost/browneye/base:r13.1-build-20261101 \
#       scripts/make_build_tools_image.sh
#
# The dnf/createrepo_c used for the install come from TOOL_IMAGE (see
# scripts/repo_tools.sh): by default the current self-hosted base image with
# the host-tool fallback.  Once this script has produced a -build image,
# pass it as TOOL_IMAGE to bootstrap_selfhosted.sh to make the next run fully
# self-hosted.
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/repo_tools.sh

DATE=$(date +%Y%m%d)
BASE_IMAGE=${BASE_IMAGE:-localhost/browneye/base:r13.1-selfhost-$DATE}
REPO=${REPO:-build/repo-selfhost}
ROOTFS=${ROOTFS:-build/rootfs-build}
TARBALL=${TARBALL:-build/rootfs-build.tar.gz}
IMAGE=${IMAGE:-localhost/browneye/base:r13.1-build-$DATE}

[ -d "$REPO" ] || { echo "missing repo: $REPO" >&2; exit 1; }
if [ ! -f "$REPO/repodata/repomd.xml" ]; then
    createrepo "$REPO"
fi

rm -rf "$ROOTFS" "$TARBALL"

dnf_install_packages "$REPO" "$ROOTFS" browneye-base browneye-build
rootfs_finalize "$ROOTFS"
rootfs_tarball "$ROOTFS" "$TARBALL"

echo "building $IMAGE from $BASE_IMAGE base system"
podman build -t "$IMAGE" -f - . <<EOF
FROM scratch
ADD ${TARBALL} /
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV LANG=C.UTF-8
ENV container=podman
WORKDIR /build
CMD ["/bin/bash"]
EOF

echo "verifying the assembly tools inside $IMAGE"
podman run --rm "$IMAGE" /usr/bin/bash -lc \
    'dnf --version; createrepo_c --version; rpm -q browneye-build; rpm -q --whatprovides libdnf'

echo "created $IMAGE"
echo "next: TOOL_IMAGE=$IMAGE ./scripts/bootstrap_selfhosted.sh <run>"
