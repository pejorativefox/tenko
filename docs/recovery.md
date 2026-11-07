# Recovery and rescue

Status: runbook based on the current installer layout.  The commands are the
same ones `tenko-installer` runs, but the full sequence has not yet been
exercised end to end on hardware.  Treat it as a checklist, not a guarantee.

Tenko is UEFI-only, the ESP is mounted at `/boot`, and the kernel and initramfs
are flat files on that ESP.  Secure Boot must be off until signing lands
(issue #3).

## 1. Boot the live media

Use the same installer ISO you installed from.  Boot it in UEFI mode (no
legacy/CSM), with Secure Boot disabled.  The live root is console-only; use
`tty1` or the serial console at 115200 baud.

If the machine will not boot the installed disk but still boots the ISO, the
problem is in the ESP, the bootloader, the kernel/initramfs or NVRAM — not the
ISO.

## 2. Find the installed partitions

```sh
lsblk -f
blkid
parted -l
```

The default layout is:

| Partition | Role | Typical mount |
|---|---|---|
| 1 | EFI System Partition (vfat, label `TENKOESP`) | `/boot` |
| 2 | swap partition or swapfile on root | — |
| 3 | root filesystem (ext4 or btrfs) | `/` |

A swapfile lives at `/swapfile` on the root filesystem; there may be no swap
partition at all.  Note the root partition and the ESP.

## 3. Mount the installed system

```sh
ROOT=/dev/nvme0n1p3          # replace
ESP=/dev/nvme0n1p1           # replace

mkdir -p /mnt/tenko
mount "$ROOT" /mnt/tenko
mkdir -p /mnt/tenko/boot
mount "$ESP" /mnt/tenko/boot

for d in dev proc sys run; do
    mount --rbind "/$d" "/mnt/tenko/$d"
done
mount -t efivarfs efivarfs /mnt/tenko/sys/firmware/efi/efivars 2>/dev/null || true

chroot /mnt/tenko /bin/bash
```

If the root filesystem is btrfs and was installed with subvolumes by a future
version, add `-o subvol=@`; the current installer uses a plain btrfs root.

## 4. Repair systemd-boot and the firmware entry

Inside the chroot:

```sh
bootctl --esp-path=/boot --no-variables install
cat /etc/kernel/cmdline
ls -l /boot/EFI/systemd/systemd-bootx64.efi /boot/EFI/BOOT/BOOTX64.EFI
ls -l /boot/loader/entries/
```

`bootctl` writes both the normal `EFI/systemd/` loader and the removable
`EFI/BOOT/BOOTX64.EFI` fallback.  If `/boot/loader/loader.conf` is missing:

```sh
mkdir -p /boot/loader/entries
cat > /boot/loader/loader.conf <<'EOF'
default tenko-*
timeout 3
console-mode keep
editor no
EOF
```

The entry is named `tenko-<kver>.conf`.  If it is missing, recreate it with the
installed kernel version and the root UUID:

```sh
KVER=$(ls /usr/lib/modules | sort -V | tail -1)
ROOT_UUID=$(blkid -s UUID -o value "$(findmnt -n -o SOURCE /)")
cat > "/boot/loader/entries/tenko-$KVER.conf" <<EOF
title Tenko Linux 6 (Workstation) ($KVER)
linux /vmlinuz-$KVER
initrd /initramfs-$KVER.img
options root=UUID=$ROOT_UUID ro rootwait
EOF
```

Paths in loader entries are relative to the ESP (`/boot`).  Also keep
`/etc/kernel/cmdline` in sync; kernel packages read it when they add entries:

```sh
echo "root=UUID=$ROOT_UUID ro rootwait" > /etc/kernel/cmdline
```

Recreate the NVRAM entry if the boot menu does not list Tenko:

```sh
efibootmgr --create --disk <esp-disk> --part <esp-partition> \
    --label "Tenko Linux" --loader '\EFI\systemd\systemd-bootx64.efi'
efibootmgr -v
```

Use the ESP's whole-disk path and partition number (`1` in the default
layout).  If `efibootmgr` fails because NVRAM is read-only, the firmware boot
menu should still offer the removable `BOOTX64.EFI` path.

## 5. Rebuild a missing or truncated initramfs

The ESP is FAT32 and has no journal.  A power loss during a kernel update can
leave an empty or truncated initramfs.  Inside the chroot:

```sh
KVER=$(ls /usr/lib/modules | sort -V | tail -1)
depmod "$KVER"
dracut --force --no-hostonly --kver "$KVER" "/boot/initramfs-$KVER.img"
ls -l "/boot/initramfs-$KVER.img"
```

If the kernel image itself is missing, reinstall the kernel packages (see
section 7) or copy a matching `vmlinuz-<kver>` back to the ESP.

## 6. Check the root filesystem

Unmount the ESP and root first, then run the checker for the filesystem:

```sh
umount /mnt/tenko/boot /mnt/tenko
fsck -f /dev/nvme0n1p3        # ext4
# btrfs check /dev/nvme0n1p3  # only when the filesystem is unmounted
```

Do not run `fsck` on a mounted filesystem.  If the root cannot be repaired,
mount a data partition and copy files off before reinstalling.

## 7. Repair packages from the repository

From a chroot with working network:

```sh
dnf --refresh upgrade
dnf reinstall linux-kernel linux-modules systemd
dracut --force --no-hostonly --kver "$(ls /usr/lib/modules | sort -V | tail -1)"
bootctl --esp-path=/boot --no-variables install
```

The repository is `https://tenko.pjfox.xyz/packages/6/`
(`/etc/yum.repos.d/tenko-6.repo`).  If DNS or TLS fails, check
`/etc/resolv.conf`, the clock and the CA store (`make-ca`).

A full reinstall is also valid: the guided installer can reuse an existing ESP
and adopt an existing data partition without formatting it.  Back up first.

## 8. Read the installer logs

The installer writes its own log to the ESP and to the installed system:

| Location | Contents |
|---|---|
| `/boot/tenko-install.log` | human-readable log from the last successful run |
| `/boot/tenko-install.jsonl` | JSON Lines command/event log |
| `/boot/tenko-install-failure.log` | log tail from a failed run |
| `/boot/tenko-install-failure.jsonl` | JSON Lines from a failed run |
| `/var/log/tenko-install/` | the same logs on the installed system |

Passwords are redacted.  From the installed system, `journalctl -b -1` shows
the previous boot if the system still reaches a login.

## 9. If nothing boots

1. Disable Secure Boot and retry.
2. Use the firmware boot menu and pick the removable/UEFI path for the ESP.
3. Boot the ISO and check that the ESP contains
   `EFI/BOOT/BOOTX64.EFI`, `loader/entries/tenko-*.conf`, `vmlinuz-*` and
   `initramfs-*.img`.
4. Re-run `bootctl --esp-path=/boot --no-variables install` and recreate the
   entry as in section 4.
5. As a last resort, reinstall and adopt the existing data partitions.

## Limits

- **No LUKS rescue path yet.**  Encrypted installs are not implemented
  (issue #21); when they are, unlock the volume before the chroot.
- **No BIOS/legacy boot.**  The media and installed system are UEFI-only.
- **Secure Boot is off by design.**  See issue #3 for signing work.
- **The ESP has no journal.**  Keep at least one known-good kernel/initramfs
  pair; the installer requires at least 256 MiB free on an reused ESP.
