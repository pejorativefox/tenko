# Testing images and installs

Every test runs the real UEFI path: QEMU with the OVMF firmware and a
GPT/ESP disk.  There is no BIOS path — the media and installed system are
UEFI-only.

## Prerequisites

- `qemu-system-x86_64` and `/dev/kvm`
- `edk2-ovmf` (`dnf install edk2-ovmf`) — provides
  `/usr/share/edk2/ovmf/OVMF_CODE.fd` and `OVMF_VARS.fd`
- `python3` (the scripts drive the QEMU monitor with a small Python helper;
  `socat` is not needed)
- a few GiB in `build/` for disk images, kernel/initrd and logs

Secure Boot must be **off**: the firmware is unsigned and the installer
refuses to proceed when Secure Boot is enabled.

## Boot matrix

| what | script | pass means |
|---|---|---|
| installer media | `scripts/qemu_test_installer.sh` | systemd-boot menu, kernel + initrd boot, `Started Tenko Linux installer`, multi-user and a console login prompt |
| unattended install | `ISO_AUTO=1 ISO_ANSWER=tests/installer-answer.json scripts/build_iso_uefi.sh` then boot the ISO | installer reports steps 1–9 and `OK`, `bootctl install` succeeds, disk boots to `tenko-test login:` |
| installed disk | QEMU with `-drive file=build/installer-test.img,if=virtio` and a fresh OVMF NVRAM | systemd-boot menu → kernel → login prompt |
| graphical session | `scripts/qemu_boot_graphical.sh` | X starts on tty1, screenshot captured in `build/xfce-screenshot.png` |
| first boot + greeter | `scripts/qemu_boot_login.sh` | first-boot password flow, LightDM greeter captured (guest `xwd` or screendump fallback) |
| direct kernel boot | `scripts/qemu_boot.sh` | serial login prompt from the installed rootfs (no UEFI) |

Pass criteria for a booted system:

- `systemctl is-system-running` prints `running` (or `degraded` only if you
  know which unit failed),
- `systemctl --failed` is empty,
- `graphical.target` is reached and the LightDM greeter appears for the
  desktop tests.

## Installer test

```sh
scripts/qemu_test_installer.sh
```

Environment: `ISO`, `DISK`, `DISKSIZE` (20G), `WAIT` (90 s), `MEM` (4096),
`VNC`, `OVMF_CODE`, `OVMF_VARS_SRC`, `OVMF_VARS`, `SERIAL`, `MON`, `SHOT`.
The script creates a blank disk, boots the ISO from `-cdrom`, waits, captures
a screendump and quits.  Logs: `build/installer-serial.log`,
`screenshot`: `build/installer-screen.ppm` (converted to `.png` when
ImageMagick is installed).

Interactive UI without an ISO: `scripts/run_installer_sim.sh` runs the real
curses installer against synthetic in-memory disks, forces dry-run, and
needs no root, UEFI firmware, network or block device.  Use
`--simulate-scenario mixed` to test adopting an existing ESP/data partition.
Every mutating command is written to `/tmp/tenko-installer-sim/plan.sh`
(override with `TENKO_SIM_DIR`).  This is the fast loop for installer UI
changes; boot the ISO only after the flow is correct.

Unattended install: build the ISO with `ISO_AUTO=1` and
`ISO_ANSWER=tests/installer-answer.json`.  The version 2 answer file writes a
layout on `/dev/vda` with a 1 GiB ESP + 2 GiB swap + ext4 root, installs the
`desktop` set, sets hostname `tenko-test` and admin `admin` (test-only
password).  Add another entry to `layout.disks` for a second disk, for
example a btrfs or ext4 data partition mounted at `/home`.
That image is a test artifact — do not use it on real hardware.

To exercise the installed disk yourself, boot the same disk with a fresh
OVMF variable store (`OVMF_VARS` copied from `OVMF_VARS_SRC`) and
`-drive file=build/installer-test.img,format=raw,if=virtio`, then log in on
the serial console.  `tests/serial_login.py [user] [password]` can drive that
login over a `-serial unix:...` socket and checks for the login prompt,
password prompt, shell prompt and requested commands.

## Tenko 6 ISO verification (2026-11-06)

Artifact: published `tenko-installer.iso`, 520,159,232 B, SHA-256
`f69c0be0efdd68377b5bcd5e2491fa91ed2d2b9d3cb4e9799955155d93766931`.
Environment: QEMU 11.1.3 with KVM and OVMF, 8 GiB guest RAM, a blank 20 GiB
virtio disk and a fresh OVMF variable store.

| check | result | evidence |
|---|---|---|
| stock ISO boots under OVMF | **PASS** | systemd-boot entry, `Tenko Linux 6 (Workstation)`, kernel 7.3.1, `Started Tenko Linux installer` |
| unattended desktop install | **PASS** | all 9 steps, `TENKO-INSTALL: OK`; 1 GiB ESP + 2 GiB swap + ext4 root on `/dev/vda` |
| installed disk boots with fresh NVRAM | **PASS** | systemd-boot menu, kernel 7.3.1, `tenko-test login:` |
| login and system state | **PASS** | admin login; `systemctl is-system-running` = `running`; `systemctl --failed` empty |
| graphical target | **PASS** | `graphical.target` and `lightdm` active; greeter captured in `build/installed-screen.png` |
| storage and swap | **PASS** | `/dev/vda3` ext4 on `/`, `/dev/vda1` vfat on `/boot`, `/dev/vda2` 2 GiB swap active |
| public package repository | **PASS** | installed `tenko-6.repo` points at `https://tenko.pjfox.xyz/packages/6/`; `dnf makecache` and `repolist` succeed |

The unattended install used a local remaster of the published ISO that only
adds `/answer.json` and the `tenko.auto=1` kernel option; the live squashfs,
kernel and initrd are unchanged.  The 8 GiB auto run was stopped after the
public mirror proved too slow, and the same installer was then run
non-interactively on the serial console with `--repo` set to the LAN mirror.
After installation the target repository file was switched to the public URL
and verified.  The auto path was also exercised directly: with only 4 GiB
guest RAM the package step failed with `curl` error 23 as the live overlay and
DNF cache exhausted tmpfs.  Desktop install tests should use at least 8 GiB.

`sshd-keygen.service` initially failed on first boot because a zero-length
host key made `ssh-keygen` prompt for overwrite.  This is fixed in
`openssh-10.6p1-3` (published); the reinstalled system reports no failed
units.

Not covered by this run: USB/`dd` boot and reuse of an existing small ESP
(issue #14), and Secure Boot (out of scope).  Local evidence:
`build/installer-serial.log`, `build/manual-install.log`,
`build/installed-serial.log`, `build/installed-screen.png`, plus the 4 GiB
failure log `build/auto-serial-fail-4g.log`.

## Graphical tests

```sh
scripts/qemu_boot_graphical.sh          # installs base + xfce-desktop
SKIP_INSTALL=1 scripts/qemu_boot_graphical.sh

scripts/qemu_boot_login.sh              # first boot + LightDM
SKIP_INSTALL=1 scripts/qemu_boot_login.sh
BUILD_ONLY=1 scripts/qemu_boot_login.sh
```

Both install from the published repository (`REPO`, default public URL) into
`build/rootfs-*`, build an ext4 image, boot it and capture the screen.  Logs
and screenshots are written under `build/`.

## Unit tests

```sh
python3 -m unittest discover -s tests -v
```

The command runs the top-level tests (build database, the no-`-devel` rule,
repository index generation) and the installer suite under
`package_specs/tenko-installer/tests/` (planner, probe, answer file, dry-run
install and simulation).  It needs no QEMU, root, network or block devices.

## Notes

- The live root is the `tenko-live` closure; the installer downloads the
  target packages from `REPO`, so a working network is part of the test.
- OVMF firmware comes from the `edk2-ovmf` package.  Passing a different
  firmware is possible via `OVMF_CODE`/`OVMF_VARS_SRC`.
- Boot logs are ANSI-heavy; `grep -a` them.
