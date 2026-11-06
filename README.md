# Tenko Linux

Tenko Linux 6 (Workstation) is a small x86_64 Linux distribution built from
the LFS/BLFS r13.1 books.  It uses systemd, a merged `/usr`, XFCE and a
UEFI-only, network-install ISO.  Packages are shipped as RPMs from a
self-hosted dnf repository; the installer downloads them while installing, so
the ISO carries no packages.  The distro release is 6; package versions roll
independently and keep their own versions.

- Public repository: <https://tenko.pjfox.xyz/packages/6/> (the Tenko 6
  repository; the old <https://repo.pjfox.xyz/packages/13.1/> path remains a
  compatibility alias)
- LAN mirror: <http://192.168.31.9/~daspork/tenko/> (the old
  `http://192.168.31.9/~daspork/browneye/` path is a symlink during the
  transition)
- Issue tracker: <https://pjfox.xyz/git/daspork/browneye/issues>

## Quick start

### 1. Download and verify the installer

```sh
curl -LO https://tenko.pjfox.xyz/iso/tenko-installer.iso
curl -LO https://tenko.pjfox.xyz/iso/tenko-installer.iso.sha256
sha256sum -c tenko-installer.iso.sha256
```

The ISO is 434 MiB.  On the LAN the mirror carries the same bytes:
`http://192.168.31.9/~daspork/tenko/iso/`.  The current published images
predate the rename and the Tenko 6 release, so they are republished under
these Tenko names at the next image rebuild.  A future rebuild may also
publish versioned `tenko-installer-6.iso` and `tenko-rootfs-6.tar.gz`
artifacts, with the unversioned names kept as aliases.

### 2. Write it to a USB stick

```sh
sudo dd if=tenko-installer.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

(Replace `/dev/sdX` with the stick — this erases it.)

### 3. Prepare the firmware

- The media is **UEFI-only**; legacy/CSM boot is not supported.
- **Disable Secure Boot.**  The bootloader is unsigned, and the installer
  refuses to run while Secure Boot is enabled.  This is expected until the
  signing work in issue #2/#3 lands.

### 4. Install

Boot the stick and follow the installer.  The recommended path is the guided
install: choose one disk, erase it or use its free space, pick ext4 or btrfs,
and the installer creates a 1 GiB ESP, a 2 GiB swapfile and the rest for `/`.
The advanced path opens a multi-disk layout editor for custom partition
layouts, adopting existing partitions, or putting `/home` on a second disk.
Both paths then ask for the package set (`desktop` installs XFCE) and an admin
account.  Installation is performed entirely from the network repository.

Requirements: x86_64 UEFI machine, a network connection during install, and
roughly 20 GiB of disk.

### 5. First boot

The installed system boots with systemd-boot into XFCE.  Log in with the admin
account created by the installer.  `dnf` is already configured
(`/etc/yum.repos.d/tenko-6.repo`) against the repository that was used
for the install, so:

```sh
sudo dnf install tenko-base      # build toolchain
sudo dnf upgrade
```

## Container rootfs

A 244 MiB rootfs tarball with the build toolchain is published for use as a
container/build image:

```sh
curl -LO https://tenko.pjfox.xyz/rootfs/tenko-rootfs.tar.gz
curl -LO https://tenko.pjfox.xyz/rootfs/tenko-rootfs.tar.gz.sha256
sha256sum -c tenko-rootfs.tar.gz.sha256
podman import tenko-rootfs.tar.gz localhost/tenko/rootfs:6
```

The pre-rename container tags stay valid until the image rebuild; see
[`docs/build.md`](docs/build.md) for the build-image tag.

## Working on Tenko

Everything is driven from this checkout:

| task | document |
|---|---|
| rebuild a package and publish it | [`docs/build.md`](docs/build.md) |
| boot/install tests, QEMU and OVMF | [`docs/testing.md`](docs/testing.md) |
| version policy and the LFS/BLFS sync tools | [`docs/versions.md`](docs/versions.md) |
| systemd-boot conversion notes | [`docs/systemd-boot.md`](docs/systemd-boot.md) |

The rules for agents and maintainers (including the "every package must be at
least the book version" policy and the publishing/mirror requirements) live in
[`AGENTS.md`](AGENTS.md).  Do not duplicate them elsewhere; link to them.
