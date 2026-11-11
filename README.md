# Tenko Linux

Tenko Linux 6 (Workstation) is a small x86_64 Linux distribution built with a
self-hosted RPM toolchain.  It uses systemd, a merged `/usr`, XFCE and a
UEFI-only, network-install ISO.  Packages are shipped as RPMs from a
self-hosted dnf repository; the installer downloads them while installing, so
the ISO carries no packages.  The distro release is 6; package versions roll
independently and keep their own versions.

- Public repository: <https://tenko.pjfox.xyz/packages/6/>
- LAN mirror: <http://192.168.31.9/~daspork/tenko/>
- Issue tracker: <https://pjfox.xyz/git/daspork/tenko/issues>

## Quick start

### 1. Download and verify the installer

```sh
curl -LO https://tenko.pjfox.xyz/iso/tenko-installer.iso
curl -LO https://tenko.pjfox.xyz/iso/tenko-installer.iso.sha256
sha256sum -c tenko-installer.iso.sha256
```

On the LAN the mirror carries the same files:
`http://192.168.31.9/~daspork/tenko/iso/`.

### 2. Write it to a USB stick

```sh
sudo dd if=tenko-installer.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

(Replace `/dev/sdX` with the stick — this erases it.)

### 3. Prepare the firmware

- The media is **UEFI-only**; legacy/CSM boot is not supported.
- **Disable Secure Boot.**  The bootloader is unsigned, and the installer
  refuses to run while Secure Boot is enabled (signing: issues #2 and #3).

### 4. Install

Boot the stick and follow the installer.  The recommended path is the guided
install: choose one disk, erase it or use its free space, pick ext4 or btrfs,
and the installer creates a 1 GiB ESP, a 2 GiB swapfile and the rest for `/`.
The advanced path opens a multi-disk layout editor for custom partition
layouts, adopting existing partitions, or putting `/home` on a second disk.
Both paths then ask for the package set (`desktop` installs XFCE) and an admin
account.  Installation is performed entirely from the network repository.
If the network is not up yet, the preflight screen offers `nmtui` (Wi-Fi or
wired), then retries the repository check; the live media carries the common
Wi-Fi firmware packs so wireless cards can appear.  nmtui runs in a UTF-8
kmscon console so Chinese and other non-ASCII SSIDs are listed and rendered.
If the installer screen does not appear, Ctrl+Alt+F2 opens a passwordless
root shell on tty2; the serial console autologins root as well, so
`journalctl -u tenko-installer` can be inspected.

Requirements: x86_64 UEFI machine, a network connection during install, and
roughly 20 GiB of disk.

### 5. First boot

The installed system boots with systemd-boot into XFCE.  Log in with the admin
account created by the installer.  Wired and wireless networking are managed
by NetworkManager, which starts on boot; `nm-applet` autostarts in the panel
(right-click its icon for the connection editor).  From a terminal, use
`nmtui` or `nmcli` to join a Wi-Fi network.  `dnf` is already configured
(`/etc/yum.repos.d/tenko-6.repo`) against the repository that was used for the
install, so:

```sh
sudo dnf install tenko-base      # build toolchain
sudo dnf upgrade
```

## Container rootfs

A rootfs tarball with the build toolchain (`tenko-base`) is published for use
as a container/build image:

```sh
curl -LO https://tenko.pjfox.xyz/rootfs/tenko-rootfs.tar.gz
curl -LO https://tenko.pjfox.xyz/rootfs/tenko-rootfs.tar.gz.sha256
sha256sum -c tenko-rootfs.tar.gz.sha256
podman import tenko-rootfs.tar.gz localhost/tenko/rootfs:6
```

Package builds do not need it: `tenko build` creates its own build images
from the repository (see [`docs/build.md`](docs/build.md)).

## Working on Tenko

Everything is driven from this checkout through `./tenko` (`./tenko help`):

| task | document |
|---|---|
| set up a build host | [`docs/build-host.md`](docs/build-host.md) |
| rebuild a package and publish it | [`docs/build.md`](docs/build.md) |
| installer flows, options and answer files | [`docs/installer.md`](docs/installer.md) |
| boot/install tests, QEMU and OVMF, unit tests | [`docs/testing.md`](docs/testing.md) |
| boot layout, recovery and rescue | [`docs/recovery.md`](docs/recovery.md) |
| suspend/resume policy and diagnostics | [`docs/suspend.md`](docs/suspend.md) |
| freedesktop compliance matrix | [`docs/freedesktop.md`](docs/freedesktop.md) |
| release identity and base manifest | [`docs/versions.md`](docs/versions.md) |
| writing a spec, packaging conventions | [`docs/rules.md`](docs/rules.md) |

The rules for agents and maintainers (version policy, publishing to both
sites, worktrees, documentation) live in [`AGENTS.md`](AGENTS.md).  Do not
duplicate them elsewhere; link to them.
