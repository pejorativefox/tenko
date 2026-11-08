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

### 2026-11-07 rebuild boot check

Artifact: published `tenko-installer.iso`, 520,372,224 B, SHA-256
`2ba9dc4fddf6f769ab519aaa3497a98de1ac348d00df13ec9351986fd890b2d5`.

Environment: QEMU 11.1.3 and OVMF 202608-2, 4 GiB guest RAM, a blank 20 GiB
virtio disk and a fresh OVMF variable store.  The host's `/dev/kvm` is
root-only, so this run used QEMU TCG (`-accel tcg,thread=multi -cpu max`)
rather than KVM.

| check | result | evidence |
|---|---|---|
| stock ISO boots under OVMF | **PASS** | systemd-boot entry, `Tenko Linux 6 (Workstation)`, kernel 7.3.1, dracut live root |
| installer service starts | **PASS** | `Started Tenko Linux installer` |
| system reaches multi-user | **PASS** | `Reached target Multi-User System`, `localhost login:` |
| failed units / emergency mode | **PASS** | no `Failed to start` or emergency lines |

Evidence: `build/installer-serial-tcg.log` and
`build/installer-screen-tcg.ppm`.  The full unattended install and graphical
checks above were not repeated for this rebuild; they remain the 2026-11-06
record.

### 2026-11-08 rebuild boot check

Artifact: published `tenko-installer.iso`, 573,976,576 B, SHA-256
`c8f7b4e288a7f39a6af3fd9f35731d5555f33cba6e383edf54367d5fc5a348ca`.

Environment: QEMU 11.1.3 and OVMF 202608-2, 4 GiB guest RAM, a blank 20 GiB
virtio disk and a fresh OVMF variable store.  The rebuild includes the
`2026-11-08` console stack (kmscon plus the Noto/Nerd font fallbacks).

| check | result | evidence |
|---|---|---|
| stock ISO boots under OVMF | **PASS** | systemd-boot entry, `Tenko Linux 6 (Workstation)`, kernel 7.3.1, dracut live root |
| installer service starts | **PASS** | `Started Tenko Linux installer` |
| kmscon replaces fbcon on tty1 | **PASS** | `Started KMS System Console on tty1` |
| system reaches multi-user | **PASS** | `Reached target Multi-User System`, `localhost login:` |
| failed units / emergency mode | **PASS** | no `Failed to start` or emergency lines |

Evidence: `build/installer-serial.log` and `build/installer-screen.ppm`.  The
full unattended install and graphical checks above were not repeated for this
rebuild; they remain the 2026-11-06 record.

## Graphical tests

```sh
scripts/qemu_boot_graphical.sh          # installs base + xfce-desktop
SKIP_INSTALL=1 scripts/qemu_boot_graphical.sh

scripts/qemu_boot_login.sh              # first boot + LightDM
SKIP_INSTALL=1 scripts/qemu_boot_login.sh
BUILD_ONLY=1 scripts/qemu_boot_login.sh
```

For the freedesktop desktop-level gate, run the same install plus the
in-guest session checks (notifications, portal, Secret Service, sound, trash,
tray, XSettings and EWMH).  Prefer the LAN mirror when it is reachable:

```sh
REPO=http://192.168.31.9/~daspork/tenko/packages/6/ \
    scripts/qemu_fdo_verify.sh
REPO=build/repo-all scripts/qemu_fdo_verify.sh   # local repository
```

`scripts/qemu_fdo_verify.sh` installs a fresh rootfs (or reuses a cached one,
see below) and logs in through LightDM autologin as an ordinary test account,
so the checks run in a real
logind session with a systemd user manager and
`DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus`.  This is the same
D-Bus activation path as a real login: the portal check waits for
`graphical-session.target` and `xfce-session.target`, then confirms that
`xdg-desktop-portal.service` is active under the user manager (the issue #48
fix).  A private `unix:path=/tmp/dbus-*` bus is never accepted as a pass.

The guest writes `build/qemu-share/fdo-check.txt` and the script exits:

| status | meaning |
|---|---|
| `0` | every check passed; hardware-only checks may be `SKIP` |
| `1` | a packaged component failed its check (`FAIL`) |
| `2` | harness failure (`HARNESS-FAIL`): no usable login session, wrong bus, or missing #48 units; LightDM/Xorg/journal diagnostics are in `fdo-check.txt` |

The script fails before booting if the installed `tenko-desktop-config` is
older than 6-6 (no `xfce-session.target`) or if a required desktop package is
missing.  `WAIT`, `SESSION_WAIT`, `TARGET_WAIT` and `DESKTOP_WAIT` bound the
host and guest timeouts; the result file is written atomically so a partial
check cannot be mistaken for a pass.  The log prints the rootfs, guest and
total phase times.

The installed package set is cached while the repository's `repomd.xml` is
unchanged: the first run installs, later runs reuse it and only rebuild the
image and boot QEMU.  Use `REBUILD_ROOTFS=1` for a forced fresh install,
`SKIP_BUILD=1` to reuse any existing rootfs, and `MEM=4096` (the default) to
change the guest memory.

The Secret Service is checked twice: a `dbus-run-session` round-trip as root
(provider packaging) and a `secret-tool` round-trip in the login session
(user keyring).  Autologin has no password for PAM to hand to
`pam_gnome_keyring`, so the guest unlocks the keyring with the test password;
if the persistent login collection does not exist, the round-trip uses the
Secret Service session collection.  The PAM hooks themselves are checked in
`/etc/pam.d/lightdm` and `/etc/pam.d/lightdm-autologin`.  To exercise the
greeter unlock end to end, disable the autologin drop-in in a test image, log
in at the LightDM greeter with the test password, and confirm that
`secret-tool lookup service tenko key test` returns without the manual
unlock.  The #48 evidence in that manual greeter login is recorded on the
issue tracker.

Both install from the published repository (`REPO`, default public URL) into
`build/rootfs-*`, build an ext4 image, boot it and capture the screen.  Logs
and screenshots are written under `build/`.

## Session integration check

`scripts/fdo_session_check.sh` checks the freedesktop session protocols from
inside a live XFCE/X11 session.  It is network-free and read-only, needs
`DISPLAY` and a reachable session bus (`DBUS_SESSION_BUS_ADDRESS`), and prints
one `PASS`/`FAIL`/`SKIP` line per check.  It requires the systemd user manager
bus (`XDG_RUNTIME_DIR/bus`): a private `dbus-launch` bus cannot activate the
portal, so it is reported as a failure rather than a pass.  It also verifies
that `graphical-session.target` and `xfce-session.target` are active, which
covers the issue #48 autostart entry:

```sh
# run as the logged-in user inside the guest
sh scripts/fdo_session_check.sh
```

The graphical QEMU test should run it inside the session after login (for
example from the session debug unit) and treat a non-zero exit as a failure.
It checks the EWMH root atoms `_NET_SUPPORTING_WM_CHECK`, `_NET_SUPPORTED`,
`_NET_CLIENT_LIST` and `_NET_ACTIVE_WINDOW`, that the supporting-window-check
target has `_NET_WM_NAME`, the `_XSETTINGS_S0` owner and its
`_XSETTINGS_SETTINGS` property, the `libstartup-notification` loader entry,
the session bus, and optionally an `xfce4-terminal` launch that publishes
`_NET_STARTUP_ID`.

Only a failed protocol check is `FAIL`.  Missing optional tools (for example
`xprop`, `busctl`/`dbus-send`, `ldconfig` or a startup-notification test
client) and an X server that does not expose the selection owner are `SKIP`
with a reason, so a minimal or headless session does not produce false
failures.  The headless packaging and Autostart 0.5 precedence checks live in
`tests/test_session_integration.py`; set `TENKO_ROOT` to an extracted root
tree to validate the real autostart payload instead of skipping it.

## Unit tests

```sh
python3 -m unittest discover -s tests -v
```

The command runs the top-level tests (build database, the no-`-devel` rule,
repository index generation, the freedesktop audit fixtures) and the installer
suite under `package_specs/tenko-installer/tests/` (planner, probe, answer
file, dry-run install and simulation).  It needs no QEMU, root, network or
block devices.

`scripts/run_checks.sh` is the local/CI entry point: it runs the unit tests,
`scripts/gen_base_requires.py --check` and the static freedesktop audit.

## Freedesktop audit

[`freedesktop.md`](freedesktop.md) is the durable compliance matrix.  The
audit prints one result per matrix row and exits non-zero only for `FAIL`
rows: findings in a row marked `implemented` are fatal, while findings in
`partial`/`gap` rows are reported as `OPEN` and owned by the linked issue.

```sh
# Built repository (validates desktop entries, AppStream, menus, MIME and icons)
python3 scripts/fdo_audit.py --rpm-dir build/repo-publish/6 --verbose

# An extracted or mounted root tree
python3 scripts/fdo_audit.py --root build/rootfs-xfce

# Static checks from a clean checkout (specs and file lists only)
python3 scripts/fdo_audit.py --no-rpm

# One or more rows while iterating
python3 scripts/fdo_audit.py --rpm-dir build/repo-publish/6 --only desktop-entry,icons
```

The full RPM audit needs `desktop-file-utils`, `appstream`, `rpm`,
`rpm2cpio` and `cpio` on the host; it is network-free and takes well under a
minute for the current repository.  `--json` adds a machine-readable report.
Set `--rpm-dir` to a staging directory (for example a wave output) to audit
freshly built packages before they are published.


## Notes

- The live root is the `tenko-live` closure; the installer downloads the
  target packages from `REPO`, so a working network is part of the test.
- OVMF firmware comes from the `edk2-ovmf` package.  Passing a different
  firmware is possible via `OVMF_CODE`/`OVMF_VARS_SRC`.
- Boot logs are ANSI-heavy; `grep -a` them.
