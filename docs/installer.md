# Installer

`tenko-installer` (package `tenko-installer`, Python 3 + ncurses, standard
library only) installs Tenko from the live ISO.  It is UEFI-only and
GPT-only, and installs the target packages from the network repository
(<https://tenko.pjfox.xyz/packages/6/> by default), so the media carries no
RPMs.  `tenko-live` is the live-root meta that pulls it in; the ISO is
built with `./tenko image iso` (see [build.md](build.md)).

## Running it

The live system starts the installer on tty1.  It can also be run by hand:

```sh
tenko-installer                       # interactive ncurses installer
tenko-installer --plain               # line-oriented mode for serial consoles
tenko-installer --answer FILE         # use an answer file
tenko-installer --non-interactive     # answer file only, no curses, serial markers
tenko-installer --dry-run --answer F  # plan and log; run no mutating command
tenko-installer --plan-json --answer F  # print the validated layout and exit
```

| option | effect |
|---|---|
| `--repo URL-or-path` | repository to install from |
| `--target DIR` | mount point for the new system (default `/mnt/tenko`) |
| `--reboot`, `--no-reboot` | reboot (or never reboot) after a non-interactive install |
| `--no-self-update` | do not offer a newer installer from the repository |
| `--simulate`, `--simulate-scenario NAME` | synthetic disks, forced dry-run (see below) |
| `--debug` | verbose logging |

Kernel command-line equivalents, set from the boot menu or by
`./tenko image iso`:

| parameter | same as |
|---|---|
| `tenko.answer=/path/answer.json` | `--answer` |
| `tenko.auto=1` | `--non-interactive` |
| `tenko.console=serial` | `--plain` |
| `tenko.dry_run=1` | `--dry-run` |

## Interactive flows

After the preflight checks the installer checks the repository.  If it is
unreachable it shows a network screen: it lists the NetworkManager devices,
opens `nmtui-connect` (in a kmscon VT with a UTF-8 locale, so non-ASCII
SSIDs work) and retries.  When the repository has a newer `tenko-installer`
than the running one, it offers to upgrade the copy in the live overlay and
restart with the same arguments (not in dry-run, simulate or
non-interactive runs).

**Guided install** (the default) asks for:

1. one target disk; other disks are not touched,
2. erase the disk, or use its free space (never deletes a partition and
   adopts an existing ESP without formatting it),
3. btrfs (default) or ext4, and a swapfile (default, 2 GiB), a swap
   partition or no swap,
4. the admin account, hostname, timezone, locale, keymap and package set
   (`desktop` or `base`).

A review page lists every deletion and creation; one confirmation starts
the install.

**Advanced installation** is a multi-disk layout editor.  Selecting a
partition opens its actions (assign/edit, delete, keep).  New partitions go
into free regions; sizes are GiB by default (`20`, `20G`, `20GiB` or
`512M`).  Existing partitions are kept unless marked for deletion.

## Answer files

An answer file drives an unattended install.  Without `--answer`, the
installer looks for one, in order, at:

1. `/run/initramfs/live/answer.json` (the root of the ISO; `ISO_ANSWER=file
   ./tenko image iso` puts it there, `ISO_AUTO=1` also sets `tenko.auto=1`),
2. QEMU `fw_cfg` entry `opt/tenko/answer.json`,
3. `answer.json` on a filesystem labelled `TENKO-ANSWER` (USB stick or
   virtual disk; mounted read-only).

The file is JSON and contains a plaintext password: keep it mode 0600 and
remove it from the media after use.  The installer never logs the password.
Unknown keys are rejected.

### Version 3: guided

```json
{
  "version": 3,
  "mode": "erase-disk",
  "disk": "/dev/vda",
  "filesystem": "btrfs",
  "swap": "swapfile",
  "package_set": "desktop",
  "hostname": "tenko",
  "timezone": "UTC",
  "locale": "C.UTF-8",
  "keymap": "us",
  "admin": {"username": "admin", "password": "change-me"},
  "confirm": {"phrase": "ERASE"}
}
```

| key | values (default) |
|---|---|
| `mode` | `erase-disk` or `free-space` (required) |
| `disk` | a `/dev/` path (required) |
| `filesystem` | `btrfs` or `ext4` (`ext4`) |
| `swap` | `swapfile`, `partition` or `none` (`swapfile`) |
| `swap_mib` | swap size in MiB (2048) |
| `encrypt` | only `false` is accepted; encryption is not implemented |

### Version 2: explicit layout

```json
{
  "version": 2,
  "layout": {
    "disks": [
      {
        "path": "/dev/vda",
        "delete_partitions": [],
        "partitions": [
          {"role": "esp",  "fstype": "vfat", "mountpoint": "/boot", "size_mib": 1024},
          {"role": "root", "fstype": "btrfs", "mountpoint": "/"}
        ]
      },
      {
        "path": "/dev/vdb",
        "partitions": [
          {"role": "data", "fstype": "ext4", "mountpoint": "/home"}
        ]
      }
    ]
  },
  "swap_mode": "swapfile",
  "package_set": "desktop",
  "hostname": "tenko",
  "admin": {"username": "admin", "password": "change-me"},
  "confirm": {"disk": "/dev/vda", "phrase": "ERASE"}
}
```

- A disk may also carry `serial` and `size_bytes`; when present they must
  match the probed disk.
- A partition is new (`role`, `fstype`, `mountpoint`, optional `size_mib`;
  omit the size to fill the remaining free region) or adopted
  (`existing_number`, `"format": false`).
- Roles: `esp`, `root`, `swap`, `data`.  Filesystems: `vfat`, `ext4`,
  `btrfs`, `swap`.  Exactly one root (`/`) and one ESP (`/boot`); mount
  points are unique.
- `swap_mode` is `partition` (default for version 2), `swapfile` or
  `none`; a `swapfile` layout must not contain a swap partition.
  `swap_mib` defaults to 2048.

### Keys common to both versions

| key | values (default) |
|---|---|
| `package_set` | `desktop` or `base` (`desktop`) |
| `hostname` | (`tenko`) |
| `timezone` | (`UTC`) |
| `locale` | (`C.UTF-8`); any other locale also installs `glibc-locales-extra` |
| `keymap` | (`us`) |
| `admin` | `username` and `password` (required) |
| `confirm` | required: `phrase` must be `ERASE`; version 2 also needs `disk`, the disk holding `/` |
| `dry_run` | `true` behaves like `--dry-run` |

`tests/installer-answer.json` is the answer file the unattended ISO test
uses.

## Layout rules and safety

- GPT only; MBR disks are refused.  The live medium, mounted, swapped,
  read-only and LVM/RAID/dm member devices are never selectable, and the
  reason is shown.
- An existing ESP can be adopted as `/boot` (with a warning when it is too
  small for systemd-boot, a kernel and an initramfs); otherwise a 1 GiB
  FAT32 ESP is created.  A new root is at least 8 GiB.
- Data partitions can be mounted at any absolute path except `/boot`,
  `/proc`, `/sys`, `/dev`, `/run` and `/tmp`.
- Before changing a disk the installer saves its partition table (text and
  raw sectors).  After writing, every untouched partition is compared; a
  mismatch restores the saved table before any filesystem is created.
- Deleting partitions, or any custom layout, requires typing the disk path
  and `ERASE`.

## What it installs

The installer partitions and formats, mounts the target, then installs
`tenko-basefs` in its own transaction followed by `tenko-base-runtime`,
`xfce-desktop` (desktop set only), the kernel and modules, dracut,
efibootmgr, dosfstools, btrfs-progs, sudo, openssh, git and dnf.  It writes
fstab by UUID, the hostname, the admin user (in `wheel` and `kvm`; root is
locked), builds a generic initramfs and installs systemd-boot to the ESP
with a fallback `EFI/BOOT/BOOTX64.EFI` and a best-effort NVRAM entry.  The
boot layout is described in [recovery.md](recovery.md).

## Logs

| path (live system) | content |
|---|---|
| `/run/tenko/install.jsonl` | one JSON event or command per line |
| `/run/tenko/install.log` | readable copy |
| `/run/tenko/plan.json` | validated layout |
| `/run/tenko/plan.sh` | command script written by a dry run |
| `/run/tenko/backup/` | saved partition tables |

After a successful install the logs are copied to
`/var/log/tenko-install/` on the target and to the ESP
(`tenko-install.jsonl`, `.log`).  After a failure the tail is copied to the
ESP as `tenko-install-failure.jsonl`/`.log`.  Passwords are redacted.

## Developing the installer

`./tenko installer-sim` runs the real curses flow, planner and install
pipeline against synthetic disks with a forced dry run: no root, firmware,
live media or block device is needed.  `--simulate-scenario mixed` adds an
existing ESP and data partition.  Planned commands go to `plan.sh` under
`/tmp/tenko-installer-sim` (`TENKO_SIM_DIR` overrides).

The installer's unit tests run with the rest of `./tenko check`; boot tests
of the ISO are in [testing.md](testing.md).
