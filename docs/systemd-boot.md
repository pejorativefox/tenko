# Converting Browneye to systemd-boot

**Status:** implemented on branch `systemd-boot`, 2026-11-04 (P0 packaging,
P1 installer/kernel, P2 ISO). Related: Gitea issue #2 (Secure Boot research,
option C).

This document covers replacing GRUB with systemd-boot (sd-boot) for both the
installed system and the installer ISO. It records the decisions taken so far,
the verified current state, the target layout, the package changes, and the
phased implementation plan.

## Decisions

1. **Add `python3-pyelftools`** (PyPI 0.33) as a build dependency so systemd
   builds its EFI bootloader. `systemd` itself is in LFS/BLFS r13.1; BLFS lists
   `pyelftools` as an optional dependency of systemd but ships no page for it,
   so this is a book-less build dependency. Recorded in issue #2.
2. **ESP mounted at `/boot`** on installed systems. sd-boot only reads FAT
   (`$BOOT` = ESP or XBOOTLDR), so kernel, initramfs and loader entries live on
   the ESP. No XBOOTLDR partition.
3. **Boot Loader Specification Type #1 entries** (separate kernel + initrd),
   not UKIs. `ukify` stays disabled, so `python-pefile` is not needed. Secure
   Boot remains out of scope per the 2026-11-03 decision on issue #2; UKIs are
   the path back to it later.
4. **Design before code.** This pass contains no build, installer or ISO
   changes.

## Why

- sd-boot is ~100 KiB, configured with plain text (`loader.conf` +
  `loader/entries/*.conf`); no grub modules, no `grub-mkstandalone`, no
  generated `grub.cfg`.
- `bootctl` and `kernel-install` already ship in the systemd package; no new
  runtime dependency.
- Native UKI support and a clean signature chain if Secure Boot is ever
  revisited (issue #2, option C).

Trade-offs accepted: no GRUB shell for recovery, boot data must live on FAT,
larger ESP usage, and one more build-time dependency.

## Verified current state

| Layer | Now |
|---|---|
| Installed bootloader | `install.py:step_bootloader` runs `grub-install --target=x86_64-efi --efi-directory=/boot/efi --boot-directory=/boot --bootloader-id=browneye --no-nvram`, writes a static `/boot/grub/grub.cfg` (`_grub_cfg`), copies `EFI/browneye/grubx64.efi` to `EFI/BOOT/BOOTX64.EFI`, adds an `efibootmgr` entry for `\EFI\browneye\grubx64.efi` |
| Partition layout | GPT: 512 MiB ESP (`ESP_MIB = 512`, FAT32 label `BROWNEYEESP`), 2 GiB swap, ext4 root filling the rest (`disk.py`) |
| Mounts / fstab | ESP mounted at `/boot/efi` (`rw,umask=0077`), fstab `/boot/efi vfat umask=0077,shortname=winnt 0 2` |
| Kernel | `linux-7.3.1`, `CONFIG_EFI_STUB=y`, bzImage at `/boot/vmlinuz-7.3.1`; `linux-modules` `%post` runs `dracut --force --kver 7.3.1 /boot/initramfs-7.3.1.img` |
| systemd | 262.1, built with `-D ukify=disabled`; `bootctl` and `kernel-install` are present |
| systemd-boot | **not built**: RPM and `build/rootfs-publish` have no `/usr/lib/systemd/boot/efi/systemd-bootx64.efi` |
| ISO | `scripts/build_iso_uefi.sh`: RPM-built live root → squashfs → `grub-mkstandalone` → 12 MiB FAT16 El Torito image + `-append_partition 2 0xef` GPT ESP; UEFI only |
| Live root package set | requires `grub`, `dracut`, `efibootmgr`, `efivar`, `dosfstools`, `LVM2` (`browneye-live.spec`) |

Measured from the current `build/browneye-installer.iso` (xorriso `lsdl`):

| File | Size |
|---|---|
| `/vmlinuz` | 15.3 MiB |
| `/initrd.img` | 32.3 MiB |
| `/EFI/BOOT/BOOTX64.EFI` (GRUB) | 4.9 MiB |
| `/LiveOS/squashfs.img` | 240 MiB |

## The blocker: sd-boot is not built

From the systemd 262.1 meson tree:

```meson
pyelftools = pymod.find_installation(
        'python3',
        required : get_option('bootloader').enabled() or want_dlopen_tests,
        modules : ['elftools'],
)

have = get_option('bootloader').require(
        pyelftools.found() and get_option('efi') and efi_arch != '',
        error_message : 'unsupported EFI arch or EFI support is disabled').allowed()
conf.set10('ENABLE_BOOTLOADER', have)
```

With `bootloader` defaulting to `auto` and no `elftools` module in the build
container, `ENABLE_BOOTLOADER` is 0 and the loader and stub are skipped
silently. gnu-efi is **not** needed; current systemd builds sd-boot with its
own freestanding EFI code.

Verified: `rpm -qpl systemd-262.1-1.x86_64.rpm | grep systemd/boot` is empty,
and the build image has neither `/usr/include/efi` nor
`/usr/lib/systemd/boot/efi`.

## Target design

### Installed system

Partitions (GPT):

| # | Size | Type | Mount |
|---|---|---|---|
| 1 | 1 GiB | EFI System (FAT32, `BROWNEYEESP`) | `/boot` |
| 2 | 2 GiB | Linux swap | swap |
| 3 | rest | Linux (ext4) | `/` |

`ESP_MIB` goes 512 → 1024. With flat kernel + initramfs (15.3 + 32.3 MiB) that
holds roughly four kernel generations; 512 MiB still works but leaves little
room for a rescue kernel and initramfs growth. Reusing an existing ESP keeps
its size (`plan_layout(reuse_existing_esp=True)`), so the installer must also
check free space and fail with a clear message below ~200 MiB free.

Boot chain:

```
firmware
  └─ /boot/EFI/systemd/systemd-bootx64.efi   (NVRAM entry "Browneye Linux")
     or /boot/EFI/BOOT/BOOTX64.EFI           (removable fallback, same binary)
        └─ /boot/loader/loader.conf
           └─ /boot/loader/entries/browneye-7.3.1.conf
              ├─ linux  /vmlinuz-7.3.1
              └─ initrd /initramfs-7.3.1.img
```

`loader/loader.conf`:

```
default browneye-*
timeout 3
console-mode keep
editor no
```

Entry (paths are relative to `$BOOT`, i.e. `/boot`):

```
title Browneye Linux 13.1 (7.3.1)
linux /vmlinuz-7.3.1
initrd /initramfs-7.3.1.img
options root=UUID=<root fs uuid> ro rootwait quiet splash
```

### Why hand-written entries instead of `kernel-install`

`kernel-install add` is the systemd-native path, but it assumes a
`machine-id` entry token, copies the kernel into `$BOOT/<token>/<kver>/linux`
(a second 15 MiB copy while the RPM already puts the kernel in `/boot`), and
its dracut hook rebuilds an initramfs that `linux-modules`' `%post` already
builds. The module package also runs its `%post` *before* the kernel package,
because `linux` requires `linux-modules`, so a `kernel-install` call from the
module scriptlet cannot rely on the kernel image being present.

Keeping flat files means:

- `linux-modules %post` keeps building `/boot/initramfs-<kver>.img` (unchanged,
  so module-only updates still refresh the initramfs);
- `linux %post` writes `/boot/loader/entries/browneye-<kver>.conf`;
- `linux %preun` removes the entry (and the existing `%preun` in modules
  removes the initramfs);
- the installer writes the same entry directly, with the root UUID it just
  formatted.

If UKIs become interesting later, this is the piece to replace with
`kernel-install` + `ukify`.

## Installer changes

`package_specs/browneye-installer/files/install.py`:

- `step_mount`: mount the ESP at `target/boot` instead of `target/boot/efi`
  (create `boot` before mounting; root fs already has an empty `/boot`).
- `_write_fstab`: `UUID=... /boot vfat umask=0077,shortname=winnt 0 2`.
- `step_bootloader` → sd-boot:
  - `chroot <target> /usr/bin/bootctl --esp-path=/boot --no-variables install`
  - write `loader/loader.conf` and `loader/entries/browneye-<kver>.conf`
    (replaces `_grub_cfg`)
  - verify `/boot/EFI/systemd/systemd-bootx64.efi` and
    `/boot/EFI/BOOT/BOOTX64.EFI` exist
  - `efibootmgr --create --disk ... --part <esp> --label "Browneye Linux"
    --loader '\EFI\systemd\systemd-bootx64.efi'`, then `efibootmgr -v`
  - keep the current best-effort behavior for read-only NVRAM
- `step_finish`: log copy to the ESP path changes from `/boot/efi` to `/boot`.
- `step_initramfs`: unchanged (`dracut` writes the flat initramfs).

`package_specs/browneye-installer/files/probe.py`: replace the `grub-install`
preflight requirement with `bootctl` (and keep `efibootmgr`, `dracut`).

Packaging:

- `browneye-installer.spec`: drop `Requires: grub`; keep `dracut`,
  `efibootmgr`, `efivar`; update the description and README.
- `browneye-live.spec`: drop `Requires: grub`; bootctl comes from systemd.
- `README.browneye-installer`: update the "install the bootloader" step.
- Keep the `grub` spec in the repository but stop depending on it. Removing it
  entirely is a separate decision (see open questions).

Tests: `test_install_dry_run.py` asserts `grub-install` in the dry-run log;
switch that assertion to `bootctl` and add one for the loader entry content.

## ISO changes

The live kernel and initramfs must live **inside** the FAT image because sd-boot
cannot read ISO9660. Scaffolding stays the same otherwise.

```
ISO9660
  /LiveOS/squashfs.img
  /EFI/BOOT/efiboot.img        El Torito image, also GPT ESP via -append_partition
  (no /grub.cfg, no /vmlinuz, no /initrd.img)

efiboot.img (96 MiB, FAT32)
  /EFI/BOOT/BOOTX64.EFI        systemd-bootx64.efi from the live root
  /loader/loader.conf
  /loader/entries/browneye.conf
  /vmlinuz
  /initrd.img
```

Sizing: kernel 15.3 + initramfs 32.3 MiB ≈ 48 MiB today, so 96 MiB (FAT32,
≥ 65525 clusters) leaves headroom for initramfs growth; the ISO grows by about
35 MiB against today's 323 MiB. If that is unacceptable, the alternative is to
drop the ISO9660 copies only (already planned) and shrink to 64 MiB.

`scripts/build_iso_uefi.sh` changes:

- copy `<live>/usr/lib/systemd/boot/efi/systemd-bootx64.efi` to
  `efiboot.img:/EFI/BOOT/BOOTX64.EFI` instead of running `grub-mkstandalone`;
- drop the GRUB standalone build and the generated `grub.cfg`;
- grow `efiboot.img` from 12 MiB FAT16 to 96 MiB FAT32 and copy kernel,
  initramfs, `loader.conf` and the entry into it with mtools;
- keep the squashfs, the live boot args
  (`root=live:CDLABEL=BROWNEYE rd.live.image rd.live.dir=LiveOS
  rd.live.squashimg=squashfs.img rd.overlay=1 console=tty0
  console=ttyS0,115200`), `ISO_AUTO`/`ISO_ANSWER`, and the final `xorrisofs`
  invocation (`-e boot/efiboot.img -no-emul-boot -append_partition 2 0xef
  -isohybrid-gpt-basdat`).

`loader.conf` for the ISO: `default browneye.conf`, `timeout 5`,
`console-mode keep`.

Live-root/ISO tooling: no new packages. `systemd` now ships the loader;
`dosfstools`/`mtools` already build the FAT image.

### Legacy paths retired

`scripts/build_iso.sh`, `scripts/build_iso_efi.sh`, `scripts/make_efi_disk.sh`
and `iso/{isolinux.cfg,grub.cfg,grub-stub.cfg}` were deleted: they referenced
syslinux under `/share`, kernel 5.6.14 and host-side dracut, none of which
match the RPM-based flow. `iso/core.repo` remains.

## Packaging: enabling sd-boot

New spec, following the existing Python module pattern (see
`package_specs/python-packaging`):

`package_specs/python3-pyelftools/python3-pyelftools.spec`

```
Name:       python3-pyelftools
Version:    0.33
Release:    1
Summary:    Python library for analysing ELF files and DWARF debugging information
License:    Public Domain
Source0:    pyelftools-%{version}.tar.gz
Prefix:     /usr

%description
...

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files
/usr/lib64/python3.15/site-packages/
```

Source0 URL: `https://files.pythonhosted.org/packages/source/p/pyelftools/pyelftools-%{version}.tar.gz`
(normalise the checksum into `package_specs/python3-pyelftools/sources`).

`package_specs/systemd/systemd.spec`:

- `BuildRequires: python3-pyelftools`
- `-D bootloader=enabled` (keep `-D ukify=disabled`)
- `-D sbat-distro-url=https://pjfox.xyz/git/daspork/browneye/issues`: SBAT
  autodetection reads `BUG_REPORT_URL` from `/etc/os-release`, which
  `browneye-release` does not set yet, so the build fails without an explicit
  URL
- `Release: 3`, changelog entry naming pyelftools and the new bootloader
- after install, assert
  `test -f %{buildroot}/usr/lib/systemd/boot/efi/systemd-bootx64.efi`, so a
  missing module cannot silently drop the loader again
- add the new payload to the static filelist: the three EFI binaries under
  `/usr/lib/systemd/boot/efi/`, plus the boot-assessment units and helpers
  (`systemd-bless-boot`, `systemd-boot-update.service`, `systemd-bootctl.*`,
  `systemd-sysupdate-notify-bootctl.*`, their `.wants` links and the
  generator)

The build image needs the module too: `scripts/make_base_image.sh` now lists
`python3-pyelftools` in its `DEVEL_PACKAGES` default, so a base image rebuilt
from the published repo can rebuild systemd.

Order of work: add pyelftools → build and publish it → rebuild systemd
262.1-3 → verify the loader in the RPM and in a fresh live root → rebuild and
publish anything that depends on it. `scripts/publish_rpm.sh` publishes to the
public site and the LAN mirror together.

## Phases

| Phase | Work | Exit criteria |
|---|---|---|
| P0 | pyelftools spec; systemd rebuild/publish | **done**: `python3-pyelftools-0.33-1` and `systemd-262.1-3` published; `rpm -qpl` shows `systemd-bootx64.efi` (UEFI architectures: x64, SBAT distro `browneye`) |
| P1 | installer, kernel entry scriptlets, fstab/mount, probe, tests | **done in code**: `browneye-installer-13.1-13`, `linux-7.3.1-2`; unit tests pass. QEMU install run still pending |
| P2 | ISO rework, retire legacy GRUB/syslinux paths | **done in code**: `scripts/build_iso_uefi.sh` builds a FAT32 ESP with sd-boot; legacy scripts/configs removed. ISO build/boot run still pending |
| P3 | cleanup: drop `grub` requirements, README/docs, decide `grub` spec fate | requirements dropped from `browneye-installer`/`browneye-live`; the `grub` spec itself is kept (open question 2) |

Per `AGENTS.md`, the ISO is rebuilt and republished only when requested, so P2
may land as code plus a local test image and the published ISO stays GRUB-based
until a rebuild is asked for. Note that in the ISO/rootfs rebuild issue.

## Verification checklist

- [ ] `rpm -qpl systemd-*.rpm | grep systemd-bootx64.efi` (main package)
- [ ] `bootctl status` on the installed system names sd-boot, the ESP at
      `/boot`, and lists the entry
- [ ] `dnf reinstall linux` writes a new `loader/entries/browneye-<kver>.conf`
- [ ] `dnf reinstall linux-modules` refreshes the initramfs the entry points at
- [ ] install onto a disk with an existing 512 MiB ESP either reuses it with a
      space warning or fails with a clear remedy
- [ ] OVMF install run (`scripts/qemu_test_installer.sh`, ISO built with
      `ISO_AUTO=1` and an `ISO_ANSWER` file) then boot the installed disk in
      OVMF; `scripts/qemu_boot.sh` boots `-kernel` directly and stays a
      payload regression, not an sd-boot test
- [ ] ISO: CD boot and `dd`-to-USB boot both reach the live root; serial
      console shows sd-boot
- [ ] `efibootmgr -v` after install shows `\EFI\systemd\systemd-bootx64.efi`
- [ ] fallback works with the NVRAM entry removed (`BOOTX64.EFI`)

## Risks

- **Small ESPs.** Kernel and initramfs are large flat files on FAT. An existing
  512 MiB ESP reused by the installer holds ~3 generations; the installer must
  check free space and the docs should tell users to prune old kernels.
- **FAT as boot storage.** No journaling; a power loss mid-dracut can leave a
  truncated initramfs. sd-boot has no recovery shell, so recovery means booting
  the live ISO and reinstalling the bootloader.
- **Unsigned chain.** sd-boot is unsigned, exactly like the current GRUB; the
  system still requires Secure Boot off (probe.py enforces it), per issue #2.
- **NVRAM quirks.** Some firmware ignores a `\EFI\systemd\` entry or has a full
  NVRAM; `bootctl install` also writes `EFI/BOOT/BOOTX64.EFI`, which is what
  those machines will use.
- **Serial/console.** sd-boot's menu must appear on `ttyS0` for QEMU tests;
  `console-mode keep` plus firmware console output should cover it, but this
  needs a real OVMF run to confirm.
- **Partition growth.** Raising `ESP_MIB` to 1024 changes new-install layouts;
  reuse of an existing ESP must not assume 1 GiB.

## Open questions

1. Is a 1 GiB default ESP acceptable, or keep 512 MiB and prune aggressively?
2. Keep the `grub` package in the repository (for users who want it) or remove
   it after the conversion is proven?
3. Retire the BIOS/syslinux paths permanently, or keep them as dead scripts?
4. Should `ukify` be enabled later for UKIs (needs `python-pefile`, and only
   matters if Secure Boot comes back into scope)?
