# Browneye Linux

Browneye is a small x86_64 Linux distribution built from the LFS/BLFS r13.1
books.  It uses systemd, a merged `/usr`, XFCE and a UEFI-only, network-install
ISO.  Packages are shipped as RPMs from a self-hosted dnf repository; the
installer downloads them while installing, so the ISO carries no packages.

- Public repository: <https://repo.pjfox.xyz/packages/13.1/>
- LAN mirror: <http://192.168.31.9/~daspork/browneye/packages/13.1/>
- Issue tracker: <https://pjfox.xyz/git/daspork/browneye/issues>

## Quick start

### 1. Download and verify the installer

```sh
curl -LO https://repo.pjfox.xyz/iso/browneye-installer.iso
curl -LO https://repo.pjfox.xyz/iso/browneye-installer.iso.sha256
sha256sum -c browneye-installer.iso.sha256
```

The ISO is 434 MiB.  On the LAN the mirror carries the same bytes:
`http://192.168.31.9/~daspork/browneye/iso/`.

### 2. Write it to a USB stick

```sh
sudo dd if=browneye-installer.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

(Replace `/dev/sdX` with the stick — this erases it.)

### 3. Prepare the firmware

- The media is **UEFI-only**; legacy/CSM boot is not supported.
- **Disable Secure Boot.**  The bootloader is unsigned, and the installer
  refuses to run while Secure Boot is enabled.  This is expected until the
  signing work in issue #2/#3 lands.

### 4. Install

Boot the stick and follow the installer.  It opens a multi-disk layout
editor: create and delete partitions, assign mount points, and optionally put
a data filesystem such as `/home` on a second disk.  The default root layout
is a 1 GiB ESP, 2 GiB swap and the rest for `/` (ext4 or btrfs).  It then asks
for the package set (`desktop` installs XFCE) and an admin account.
Installation is performed entirely from the network repository.

Requirements: x86_64 UEFI machine, a network connection during install, and
roughly 20 GiB of disk.

### 5. First boot

The installed system boots with systemd-boot into XFCE.  Log in with the admin
account created by the installer.  `dnf` is already configured
(`/etc/yum.repos.d/browneye-13.1.repo`) against the repository that was used
for the install, so:

```sh
sudo dnf install browneye-base      # build toolchain
sudo dnf upgrade
```

## Container rootfs

A 244 MiB rootfs tarball with the build toolchain is published for use as a
container/build image:

```sh
curl -LO https://repo.pjfox.xyz/rootfs/browneye-rootfs.tar.gz
curl -LO https://repo.pjfox.xyz/rootfs/browneye-rootfs.tar.gz.sha256
sha256sum -c browneye-rootfs.tar.gz.sha256
podman import browneye-rootfs.tar.gz localhost/browneye/rootfs:13.1
```

## Working on Browneye

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
