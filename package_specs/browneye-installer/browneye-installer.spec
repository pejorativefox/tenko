Name:       browneye-installer
Version:    13.1
Release:    23
Summary:    Browneye Linux 13.1 installer (Python + ncurses)
License:    MIT
BuildArch:  noarch
Prefix:     /usr

# Runtime tools the installer invokes directly.  browneye-live pulls in the
# complete live environment; these make a standalone install coherent too.
Requires:   python
Requires:   ncurses
Requires:   util-linux
Requires:   e2fsprogs
Requires:   dosfstools
Requires:   btrfs-progs
Requires:   dnf
Requires:   dracut
Requires:   efibootmgr
Requires:   efivar
Requires:   coreutils
Requires:   systemd

%description
A Python 3 / ncurses installer for Browneye Linux 13.1.

It is UEFI-only and GPT-only.  The default guided install erases one disk
(or uses its free space), creates a 1 GiB ESP and a root filesystem with a
swapfile, and optionally uses btrfs.  The advanced multi-disk layout editor
creates and deletes partitions on any number of GPT disks, assigns mount
points (for example /home on a second disk), and adopts existing partitions
without formatting them.  One root and one ESP are required; any number of
data partitions can be mounted at absolute paths.  Filesystems are ext4,
btrfs, vfat and swap.  The ESP is mounted at /boot and carries systemd-boot,
the kernel and the initramfs.  The target is browneye-base + xfce-desktop +
kernel/modules + dracut/efibootmgr/dosfstools/btrfs-progs/dnf, installed
with dnf --installroot after browneye-basefs.

The disk layer is a pure planner: it parses sfdisk --json and lsblk --json,
computes free regions including the GPT tail gap, renders the complete
replacement table, verifies preservation and emits commands for the runner.
--dry-run executes no mutating command.  Every command and exit status is
logged as JSON Lines and mirrored to the console; the log is copied to the
ESP at the end.

The package also ships the live systemd unit, the preset that masks the
first-boot root-password prompt, and the dracut dmsquash-live configuration.

%prep

%build

%install
rm -rf %{buildroot}
install -vdm755 %{buildroot}%{_bindir}
install -vdm755 %{buildroot}/usr/lib/browneye-installer

install -vm755 %{_sourcedir}/browneye-installer \
    %{buildroot}%{_bindir}/browneye-installer

for module in log.py runner.py disk.py layout.py probe.py simulate.py install.py ui.py main.py; do
    install -vm644 %{_sourcedir}/"$module" \
        %{buildroot}/usr/lib/browneye-installer/"$module"
done

install -vdm755 %{buildroot}%{_unitdir}
install -vm644 %{_sourcedir}/browneye-installer.service \
    %{buildroot}%{_unitdir}/browneye-installer.service

install -vdm755 %{buildroot}/usr/lib/systemd/system-preset
install -vm644 %{_sourcedir}/90-browneye-live.preset \
    %{buildroot}/usr/lib/systemd/system-preset/90-browneye-live.preset

install -vdm755 %{buildroot}/usr/lib/dracut/dracut.conf.d
install -vm644 %{_sourcedir}/20-browneye-live.conf \
    %{buildroot}/usr/lib/dracut/dracut.conf.d/20-browneye-live.conf

install -vdm755 %{buildroot}%{_docdir}/browneye-installer
install -vm644 %{_sourcedir}/README.browneye-installer \
    %{buildroot}%{_docdir}/browneye-installer/README

%files
%dir /usr/lib/browneye-installer
/usr/lib/browneye-installer/*.py
%{_bindir}/browneye-installer
%{_unitdir}/browneye-installer.service
/usr/lib/systemd/system-preset/90-browneye-live.preset
/usr/lib/dracut/dracut.conf.d/20-browneye-live.conf
%{_docdir}/browneye-installer/README

%changelog
* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-23
- Add a guided install path: choose one disk, erase it or use its free
  space, pick ext4/btrfs and swapfile/swap-partition/no-swap, then review
  and install.  The advanced multi-disk editor remains available.
- Add plan_erase_disk() and plan_free_space() to the pure layout planner.
- Make the advanced partition editor act on the selected row: Enter opens
  assign/edit, delete and keep actions, and the assign/delete menus no
  longer require typing a partition number.
- Accept GiB sizes in the new-partition form (20, 20G, 20GiB, 512M) and
  keep form input after validation errors.
- Default to a 2 GiB swapfile instead of a swap partition; add swap_mode /
  swap_mib to InstallConfig and the answer file.  A swap partition is still
  accepted (and is required for the partition mode).
- Add a proportional disk map to the disk picker, guided method screen and
  layout editor, with ESP/Windows/Linux/free labels.
- Add optional colour to the ncurses UI; NO_COLOR keeps the mono output.
- Fix the root-disk wording and make selection order explicit.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-22
- Do not offer floppy (fd*), optical (sr*), loop, ram and zram devices as
  installation targets, and reject disks smaller than 1 GiB.  A QEMU boot
  showed /dev/fd0 (4 KiB) as the first selectable disk, ahead of the real
  virtio target.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-21
- Add --simulate / --simulate-scenario: run the real curses UI, planner
  and install pipeline against synthetic in-memory disks, with the command
  runner forced to dry-run.  No root, UEFI, network or block device is
  needed; logs/plan.sh go to /tmp/browneye-installer-sim (override with
  BROWNEYE_SIM_DIR).
- Add scripts/run_installer_sim.sh and the "mixed" scenario with an
  existing ESP and ext4 data partition for adoption testing.
- Ship simulate.py.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-20
- Fix the interactive flow after disk setup: validate only the layout at
  that point.  The full config.validate() rejected the still-empty admin
  password and silently returned to disk selection, so the account form
  was never shown and installation could not start.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-19
- Repository preflight: send a "Browneye-Installer/13.1" User-Agent.
  Cloudflare/R2 returns HTTP 403 to urllib's default Python-urllib UA,
  which made every install fail at preflight even though dnf could fetch
  the same metadata.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-18
- Validate data mount points to a safe absolute-path character set before
  they reach fstab, and require the v2 "format" field to be a JSON boolean.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-17
- Default an adopted existing partition in a v2 answer file to format=false:
  adopting an entry must not reformat its data unless "format": true is
  explicit.
- On a partition write/verification failure, roll back every disk written
  in this run, not only the disk that failed.
- Refine the layout editor: handle Esc on the disk-selection screen, show the
  free regions, allow reformatting an assigned existing partition, and reject
  duplicate root/ESP roles immediately.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-16
- Replace the single-disk ESP/swap/root planner with a multi-disk layout
  editor (layout.py): create/delete partitions and assign mount points on
  any number of GPT disks, adopt existing partitions without formatting,
  and mount data filesystems such as /home on a second disk.
- Add btrfs support (mkfs.btrfs, fstab, UUID mount) alongside ext4, vfat
  and swap.  Require btrfs-progs (BLFS r13.1 7.3).
- Replace answer-file version 1 with version 2: a "layout" object holds a
  "disks" array, each with delete_partitions and per-partition
  role/fstype/mountpoint/size_mib/existing_number.
- The install pipeline partitions, formats and verifies every disk in the
  layout, mounts all data partitions and swap, writes the complete fstab,
  and keeps the bootloader on the ESP of whichever disk carries /boot.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-15
- Point the default repository at https://repo.pjfox.xyz/packages/13.1/
  after moving the public tree to Cloudflare R2.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 13.1-14
- Replace GRUB with systemd-boot: mount the ESP at /boot instead of
  /boot/efi, run `bootctl --esp-path=/boot --no-variables install`, write
  loader/loader.conf and loader/entries/browneye-<kver>.conf by UUID, and
  point the efibootmgr entry at \EFI\systemd\systemd-bootx64.efi.  Write
  /etc/kernel/cmdline so kernel packages can add entries for future
  kernels.
- Default ESP size is 1 GiB (sd-boot keeps the kernel and initramfs on it)
  and an existing ESP with less than 256 MiB free is refused.
- Drop the grub dependency and package from the target set; probe for
  bootctl instead of grub-install, and update the Secure Boot preflight
  message (the bootloader is systemd-boot now).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 13.1-11
- Write /etc/yum.repos.d/browneye-13.1.repo on the target with the
  repository the install used (same id as the shipped file, so it replaces
  it instead of duplicating it).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 13.1-10
- Preflight: fetch the repository metadata (with retries) instead of
  calling os.path.isfile() on a URL.  The network repo made every
  preflight fail with "package repository: https://.../repomd.xml".
  Also order the installer after network-online.target.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 13.1-9
- Accept an http(s)/ftp URL for the repository in config validation (the
  default is now a URL, so 13.1-8 rejected its own default).  Fixes the
  dry-run/runner tests, which also expected the old browneye-base target.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 13.1-8
- Install from the network repository by default
  (https://tomfool.8bit.ca/browneye/packages/13.1/).  `--repo`/the answer
  file still accept a local path; a URL is passed to dnf unchanged.
- Drop the post-install copy of the media repository to
  /var/lib/browneye/repo and the browneye-local.repo file.  Installing and
  using a system now requires network access (user decision), and the
  media no longer carries packages (642 -> ~320 MiB ISO).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 13.1-7
- Install browneye-base-runtime instead of browneye-base: the install media
  and the installed desktop no longer carry the compiler/toolchain
  (gcc, binutils, autotools, bison/flex, ninja, pkgconf, ...).  The full
  build-capable meta is still one `dnf install browneye-base` away from the
  network repository.
- Drop opencode-bin and herdr from the default target set; they are
  developer extras and are still available from the network repository.
  This keeps the on-ISO repository free of developer tools (saves ~270 MiB
  of media).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-6
- Install opencode-bin and herdr by default
- Copy the install media's package repository to /var/lib/browneye/repo
  and write a local file:// repo, so the installed system can dnf install
  build tooling and extras offline

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-5
- Mount a BROWNEYE-ANSWER medium read-only before reading its answer.json
  (/dev/disk/by-label/X is a block-device symlink, not a directory)
- Verified end to end: the installer UI installs to a blank GPT disk and
  the installed system boots UEFI to the LightDM greeter

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-4
- Wait up to 15 s for the answer file: the live system can start the
  installer before udev creates /dev/disk/by-label for the answer disk
- Fix the test sys.path so test_answer/test_probe import the real modules

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-3
- Never read device nodes, FIFOs or sockets: /run/initramfs/livedev is a
  symlink to the live block device on dracut-ng, and following it read the
  whole ISO into memory (OOM-killed).  Resolve the link instead; add
  regression tests.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-2
- Give the admin user a rootless container id range (usermod
  --add-subuids/--add-subgids) so podman works without manual setup

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-1
- New package: Python 3/ncurses installer with a pure GPT planner,
  snapshot/rollback, JSONL logging, dry-run, answer files and the live
  systemd/preset/dracut integration.
- UEFI-only, GPT-only MVP; reuses an existing ESP; ext4 root (8 GiB min)
  plus 2 GiB swap; basefs-first dnf installroot target.
- Live unit masks the first-boot root-password service on tty1.
