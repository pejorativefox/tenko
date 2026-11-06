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
| installer media | `scripts/qemu_test_installer.sh` | systemd-boot menu, kernel + initrd boot, `Started Browneye Linux installer`, multi-user and a console login prompt |
| unattended install | `ISO_AUTO=1 ISO_ANSWER=tests/installer-answer.json scripts/build_iso_uefi.sh` then boot the ISO | installer reports steps 1–9 and `OK`, `bootctl install` succeeds, disk boots to `browneye-test login:` |
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
Every mutating command is written to `/tmp/browneye-installer-sim/plan.sh`
(override with `BROWNEYE_SIM_DIR`).  This is the fast loop for installer UI
changes; boot the ISO only after the flow is correct.

Unattended install: build the ISO with `ISO_AUTO=1` and
`ISO_ANSWER=tests/installer-answer.json`.  The version 2 answer file writes a
layout on `/dev/vda` with a 1 GiB ESP + 2 GiB swap + ext4 root, installs the
`desktop` set, sets hostname `browneye-test` and admin `admin` (test-only
password).  Add another entry to `layout.disks` for a second disk, for
example a btrfs or ext4 data partition mounted at `/home`.
That image is a test artifact — do not use it on real hardware.

To exercise the installed disk yourself, boot the same disk with a fresh
OVMF variable store (`OVMF_VARS` copied from `OVMF_VARS_SRC`) and
`-drive file=build/installer-test.img,format=raw,if=virtio`, then log in on
the serial console.  `tests/serial_login.py [user] [password]` can drive that
login over a `-serial unix:...` socket and checks for the login prompt,
password prompt, shell prompt and requested commands.

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

The tests cover the build database, the no-`-devel` rule and the repository
index generation; they do not need QEMU.

## Notes

- The live root is the `browneye-live` closure; the installer downloads the
  target packages from `REPO`, so a working network is part of the test.
- OVMF firmware comes from the `edk2-ovmf` package.  Passing a different
  firmware is possible via `OVMF_CODE`/`OVMF_VARS_SRC`.
- Boot logs are ANSI-heavy; `grep -a` them.
