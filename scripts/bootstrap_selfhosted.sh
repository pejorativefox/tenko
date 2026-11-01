#!/usr/bin/env bash
# Assemble a clean repo from a successful container rebuild, install a fresh
# rootfs from those RPMs, and turn it into a new base image.  This is the
# second-generation check: the new image must not depend on host-built RPMs.
#
# Usage:
#   scripts/bootstrap_selfhosted.sh build/container-rebuild-20261031-2
#
# The kernel RPMs are optional; they are copied in so qemu_boot.sh can be run
# against the resulting image/rootfs, but browneye-base does not require them.
set -euo pipefail
cd "$(dirname "$0")/.."

RUN=${1:?usage: $0 build/container-rebuild-YYYYMMDD-N}
REPO=${REPO:-build/repo-selfhost}
ROOTFS=${ROOTFS:-build/rootfs-selfhost}
TARBALL=${TARBALL:-build/rootfs-selfhost.tar.gz}
IMAGE=${IMAGE:-localhost/browneye/base:r13.1-selfhost-$(date +%Y%m%d)}

if [ ! -d "$RUN/status" ]; then
    echo "missing status directory: $RUN/status" >&2
    exit 1
fi
if grep -h '^fail' "$RUN"/status/* >/dev/null 2>&1; then
    echo "refusing to bootstrap: the rebuild has failed packages" >&2
    grep -h '^fail' "$RUN"/status/* | sort >&2
    exit 1
fi

rm -rf "$REPO" "$ROOTFS" "$TARBALL"
mkdir -p "$REPO"

echo "collecting rebuilt RPMs from $RUN"
find "$RUN/build" -type f -path '*/RPMS/*/*.rpm' -exec cp -t "$REPO" {} +
# Keep the phase-2 kernel available for the boot test, but it is not a
# browneye-base dependency.
for rpm in "$HOME"/rpmbuild/RPMS/x86_64/linux-kernel-7.2.6-*.rpm \
           "$HOME"/rpmbuild/RPMS/x86_64/linux-modules-7.2.6-*.rpm; do
    if [ -f "$rpm" ]; then
        cp "$rpm" "$REPO/"
    fi
done
echo "repo RPMs: $(find "$REPO" -maxdepth 1 -name '*.rpm' | wc -l)"
createrepo_c --quiet "$REPO"

echo "installing fresh rootfs from rebuilt RPMs"
unshare -r dnf -y --nogpgcheck \
    --installroot "$PWD/$ROOTFS" --releasever=13.1 \
    --disablerepo='*' --repofrompath=selfhost,file://$PWD/$REPO \
    --setopt=install_weak_deps=False --setopt=tsflags=noscripts \
    install browneye-base

if [ -x "$ROOTFS/usr/bin/systemd-sysusers" ]; then
    unshare -r chroot "$ROOTFS" /usr/bin/systemd-sysusers || true
fi

# Apply the systemd unit presets (networkd, resolved, timesyncd, getty, ...)
# the same way LFS chapter 8 does.  systemctl --root works offline without a
# running PID 1.
if [ -x "$ROOTFS/usr/bin/systemctl" ]; then
    unshare -r chroot "$ROOTFS" /usr/bin/systemctl --root=/ preset-all || true
fi

echo "packing $ROOTFS"
unshare -r tar -C "$ROOTFS" -czf "$TARBALL" .

echo "building $IMAGE"
podman build -t "$IMAGE" -f - . <<'EOF'
FROM scratch
ADD build/rootfs-selfhost.tar.gz /
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV LANG=C.UTF-8
ENV container=podman
WORKDIR /build
CMD ["/bin/bash"]
EOF

podman run --rm "$IMAGE" /usr/bin/bash -lc \
    'gcc --version | head -1; rpmbuild --version; python3 -m pip --version; rpm -qa | wc -l'
echo "created $IMAGE"
echo "next: IMAGE=$IMAGE OUT=build/container-rebuild-selfhost scripts/verify_base_in_container.sh"
