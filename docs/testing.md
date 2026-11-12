# Testing images and installs

The installer tests run under QEMU with the OVMF firmware and a GPT/ESP
disk, the same UEFI path as real hardware.  The system tests (`tenko qemu
boot`, `login`, `fdo`, `run`) boot a test image directly with its kernel and
initramfs.  There is no BIOS path: the media and installed system are
UEFI-only.

## Prerequisites

- `qemu-system-x86_64` and `/dev/kvm`
- `edk2-ovmf` (`dnf install edk2-ovmf`) — provides
  `/usr/share/edk2/ovmf/OVMF_CODE.fd` and `OVMF_VARS.fd`
- `python3` (the scripts drive the QEMU monitor with a small Python helper)
- a few GiB in `build/` for disk images, kernel/initrd and logs

Secure Boot must be **off**: the firmware is unsigned and the installer
refuses to proceed when Secure Boot is enabled.

## Boot matrix

| what | script | pass means |
|---|---|---|
| installer media | `tenko qemu installer` | systemd-boot menu, kernel + initrd boot, `Started Tenko Linux installer`, multi-user and a console login prompt |
| unattended install | `ISO_AUTO=1 ISO_ANSWER=tests/installer-answer.json tenko image iso` then boot the ISO | installer reports steps 1–9 and `OK`, `bootctl install` succeeds, disk boots to `tenko-test login:` |
| installed disk | QEMU with `-drive file=build/installer-test.img,if=virtio` and a fresh OVMF NVRAM | systemd-boot menu → kernel → login prompt |
| recovery runbook | manual QEMU/OVMF: live image plus a throwaway installed disk ([recovery.md](recovery.md)) | each scenario ends at the installed system's login prompt |
| base system | `tenko qemu boot` | the installer's `base` package set boots to a serial login prompt; units that failed are listed |
| first boot + greeter | `tenko qemu login` | first-boot password flow, LightDM greeter captured (guest `xwd` or screendump fallback) |
| freedesktop gate | `tenko qemu fdo` | every desktop check passes in a real login session (see below) |

Pass criteria for a booted system:

- `systemctl is-system-running` prints `running` (or `degraded` only if you
  know which unit failed),
- `systemctl --failed` is empty,
- `graphical.target` is reached and the LightDM greeter appears for the
  desktop tests.

## Installer test

```sh
./tenko qemu installer
```

Environment: `ISO`, `DISK`, `DISKSIZE` (20G), `WAIT` (90 s), `MEM` (4096),
`VNC`, `OVMF_CODE`, `OVMF_VARS_SRC`, `OVMF_VARS`, `SERIAL`, `MON`, `SHOT`.
The script creates a blank disk, boots the ISO from `-cdrom`, waits, captures
a screendump and quits.  Logs: `build/installer-serial.log`,
`screenshot`: `build/installer-screen.ppm` (converted to `.png` when
ImageMagick is installed).

For installer UI changes, iterate with `./tenko installer-sim` first and
boot the ISO only once the flow is right (see
[installer.md](installer.md#developing-the-installer)).

Unattended install: build the ISO with `ISO_AUTO=1` and
`ISO_ANSWER=tests/installer-answer.json`.  That answer file erases
`/dev/vda` (1 GiB ESP, 2 GiB swap, ext4 root), installs the `desktop` set as
hostname `tenko-test` with admin `admin` and a test-only password; the
format is described in [installer.md](installer.md#answer-files).  The
image is a test artifact — do not use it on real hardware.  Give a
desktop install at least 8 GiB of guest RAM: the live overlay and the DNF
cache share tmpfs, and 4 GiB runs out during the package step.

To exercise the installed disk yourself, boot the same disk with a fresh
OVMF variable store (`OVMF_VARS` copied from `OVMF_VARS_SRC`) and
`-drive file=build/installer-test.img,format=raw,if=virtio`, then log in on
the serial console.  `tests/serial_login.py [user] [password]` can drive that
login over a `-serial unix:...` socket and checks for the login prompt,
password prompt, shell prompt and requested commands.

## Recovery checks

The commands in [recovery.md](recovery.md) are checked on a throwaway UEFI
install.  Break the install the way the scenario describes (empty initramfs,
missing loader entry, empty NVRAM), boot a live image with the installed disk
attached and run the runbook.  Each repair passes when the installed disk
boots to its login prompt.  For the filesystem check, pass means the root is
unmounted, `fsck` does not report `/dev/... is in use`, and it finishes with a
clean filesystem.  For the firmware check, `bootctl status` reports Secure
Boot disabled and `/sys/firmware/efi` exists.

Use a fresh OVMF variable store for the empty-NVRAM case; after `efibootmgr`
creates the entry, the installed disk must still boot with
`EFI/BOOT/BOOTX64.EFI` removed.

## System tests

```sh
./tenko qemu boot               # base package set, serial login prompt
./tenko qemu login              # desktop: first boot + LightDM greeter
IMAGE_ONLY=1 ./tenko qemu login # build the desktop image only
./tenko qemu run                # boot the desktop image interactively
./tenko qemu fdo                # freedesktop gate (below)
```

Each test installs exactly the package set `tenko-installer` installs
(`base` or `desktop`, taken from the installer itself) into `build/rootfs-*`
with scriptlets enabled, builds an ext4 image and boots it with KVM.  The
packages come from the offline mirror (`tenko sync`), so a run is offline
after the first sync; `REPO=URL-or-path` installs from elsewhere.  The
installed tree is reused while the repository and the package list are
unchanged; `REBUILD_ROOTFS=1` forces a fresh install.  Logs, images and
screenshots are written under `build/`, and VNC is on `127.0.0.1:5901` while
a test runs.  The shared helpers are in `scripts/lib/qemu.sh`; files
installed into the guest live in `scripts/qemu/guest/`.

## Freedesktop gate

`tenko qemu fdo` boots the desktop image and runs the in-guest session checks
(notifications, portal, Secret Service, sound, trash, tray, XSettings and
EWMH).  It logs in through LightDM autologin as an ordinary test account, so
the checks run in a real
logind session with a systemd user manager and
`DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus`.  This is the same
D-Bus activation path as a real login: the portal check waits for
`graphical-session.target` and `xfce-session.target`, then confirms that
`xdg-desktop-portal.service` is active under the user manager.
A private `unix:path=/tmp/dbus-*` bus is never accepted as a pass.

The guest writes `build/qemu-share/fdo-check.txt` and the script exits:

| status | meaning |
|---|---|
| `0` | every check passed; hardware-only checks may be `SKIP` |
| `1` | a packaged component failed its check (`FAIL`) |
| `2` | harness failure (`HARNESS-FAIL`): no usable login session, wrong bus, or missing session-target units; LightDM/Xorg/journal diagnostics are in `fdo-check.txt` |

The script fails before booting if the image lacks the XFCE session targets
from `tenko-desktop-config` or a required desktop package.  `WAIT`, `SESSION_WAIT`, `TARGET_WAIT` and `DESKTOP_WAIT` bound the
host and guest timeouts; the result file is written atomically so a partial
check cannot be mistaken for a pass.  The log prints the rootfs, guest and
total phase times.

The guest scripts are reinstalled into the image on every run, so changing
them needs no fresh install.  The guest has 4096 MiB by default (`MEM`).

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
unlock.


## Session integration check

`scripts/qemu/fdo_session_check.sh` checks the freedesktop session protocols from
inside a live XFCE/X11 session.  It is network-free and read-only, needs
`DISPLAY` and a reachable session bus (`DBUS_SESSION_BUS_ADDRESS`), and prints
one `PASS`/`FAIL`/`SKIP` line per check.  It requires the systemd user manager
bus (`XDG_RUNTIME_DIR/bus`): a private `dbus-launch` bus cannot activate the
portal, so it is reported as a failure rather than a pass.  It also verifies
that `graphical-session.target` and `xfce-session.target` are active (the
session-target autostart entry from `tenko-desktop-config`):

```sh
# run as the logged-in user inside the guest
scripts/qemu/fdo_session_check.sh
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

It runs the top-level tests under `tests/` (packaging defaults, the
no-`-devel` rule, build and publish tooling, the freedesktop audit fixtures)
and, through `tests/test_installer_suite.py`, the installer suite under
`package_specs/tenko-installer/tests/` (planner, probe, answer file, dry-run
install and guided UI).  It needs no QEMU, root, network or block devices.

`tenko check` is the local/CI entry point: it runs the unit tests,
`tenko base-requires --check` and the static freedesktop audit.

## Freedesktop audit

[`freedesktop.md`](freedesktop.md) is the durable compliance matrix.  The
audit prints one result per matrix row and exits non-zero only for `FAIL`
rows: findings in a row marked `implemented` are fatal, while findings in
`partial`/`gap` rows are reported as `OPEN` and owned by the linked issue.

```sh
# Built repository (validates desktop entries, AppStream, menus, MIME and icons)
./tenko audit --rpm-dir build/repo-publish/6 --verbose

# An extracted or mounted root tree
./tenko audit --root build/rootfs-xfce

# Static checks from a clean checkout (specs and file lists only)
./tenko audit --no-rpm

# One or more rows while iterating
./tenko audit --rpm-dir build/repo-publish/6 --only desktop-entry,icons
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
