Name:       tenko-installer
Version:    6
Release:    15
Epoch:      1
Summary:    Tenko Linux 6 (Workstation) installer (Python + ncurses)
License:    MIT
BuildArch:  noarch
Prefix:     /usr

# Runtime tools the installer invokes directly.  tenko-live pulls in the
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
Requires:   kmscon
Requires:   font-noto-cjk

%description
A Python 3 / ncurses installer for Tenko Linux 6 (Workstation).

It is UEFI-only and GPT-only.  The default guided install erases one disk
(or uses its free space), creates a 1 GiB ESP and a btrfs root filesystem
with a swapfile; ext4 is also offered.  The advanced multi-disk layout editor
creates and deletes partitions on any number of GPT disks, assigns mount
points (for example /home on a second disk), and adopts existing partitions
without formatting them.  One root and one ESP are required; any number of
data partitions can be mounted at absolute paths.  Filesystems are ext4,
btrfs, vfat and swap.  The ESP is mounted at /boot and carries systemd-boot,
the kernel and the initramfs.  The target is tenko-base + xfce-desktop +
kernel/modules + dracut/efibootmgr/dosfstools/btrfs-progs/dnf, installed
with dnf --installroot after tenko-basefs.

The disk layer is a pure planner: it parses sfdisk --json and lsblk --json,
computes free regions including the GPT tail gap, renders the complete
replacement table, verifies preservation and emits commands for the runner.
--dry-run executes no mutating command.  Every command and exit status is
logged as JSON Lines and mirrored to the console; the log is copied to the
ESP at the end.

The package also ships the live systemd unit, the preset that masks the
first-boot root-password prompt, and the dracut dmsquash-live configuration
(including the fallback that finds the ISO on a Ventoy data partition).
On the live medium the curses flow can update the running installer from
the package repository and restart itself, so an older ISO picks up the
current installer without a rebuild.

%prep

%build

%install
rm -rf %{buildroot}
install -vdm755 %{buildroot}%{_bindir}
install -vdm755 %{buildroot}/usr/lib/tenko-installer

install -vm755 %{_sourcedir}/tenko-installer \
    %{buildroot}%{_bindir}/tenko-installer

for module in log.py runner.py disk.py layout.py probe.py simulate.py install.py ui.py selfupdate.py main.py; do
    install -vm644 %{_sourcedir}/"$module" \
        %{buildroot}/usr/lib/tenko-installer/"$module"
done

install -vdm755 %{buildroot}%{_unitdir}
install -vm644 %{_sourcedir}/tenko-installer.service \
    %{buildroot}%{_unitdir}/tenko-installer.service

install -vdm755 %{buildroot}/usr/lib/systemd/system-preset
install -vm644 %{_sourcedir}/45-tenko-live.preset \
    %{buildroot}/usr/lib/systemd/system-preset/45-tenko-live.preset

install -vdm755 %{buildroot}/usr/lib/dracut/dracut.conf.d
install -vm644 %{_sourcedir}/20-tenko-live.conf \
    %{buildroot}/usr/lib/dracut/dracut.conf.d/20-tenko-live.conf

install -vdm755 %{buildroot}/usr/lib/dracut/modules.d/95tenko-ventoy
install -vm755 %{_sourcedir}/95tenko-ventoy.module-setup.sh \
    %{buildroot}/usr/lib/dracut/modules.d/95tenko-ventoy/module-setup.sh
install -vm755 %{_sourcedir}/95tenko-ventoy.iso-scan.sh \
    %{buildroot}/usr/lib/dracut/modules.d/95tenko-ventoy/tenko-ventoy-iso.sh
install -vm644 %{_sourcedir}/95tenko-ventoy.rules \
    %{buildroot}/usr/lib/dracut/modules.d/95tenko-ventoy/tenko-ventoy.rules

install -vdm755 %{buildroot}%{_docdir}/tenko-installer
install -vm644 %{_sourcedir}/README.tenko-installer \
    %{buildroot}%{_docdir}/tenko-installer/README

%files
%dir /usr/lib/tenko-installer
/usr/lib/tenko-installer/*.py
%{_bindir}/tenko-installer
%{_unitdir}/tenko-installer.service
/usr/lib/systemd/system-preset/45-tenko-live.preset
/usr/lib/dracut/dracut.conf.d/20-tenko-live.conf
%dir /usr/lib/dracut/modules.d/95tenko-ventoy
/usr/lib/dracut/modules.d/95tenko-ventoy/module-setup.sh
/usr/lib/dracut/modules.d/95tenko-ventoy/tenko-ventoy-iso.sh
/usr/lib/dracut/modules.d/95tenko-ventoy/tenko-ventoy.rules
%{_docdir}/tenko-installer/README

%changelog
* Mon Nov 09 2026 tenko <build@tenko.invalid> 6-15
- Make btrfs the first and default choice on the guided filesystem screen;
  ext4 moves to second place.  The review screen and install pipeline are
  unchanged, and plain/advanced/answer-file flows keep their explicit
  filesystem selection.

* Mon Nov 09 2026 tenko <build@tenko.invalid> 6-14
- Update the running installer from the network.  Once the repository is
  reachable, the curses flow compares the installed tenko-installer with
  the repository (`dnf repoquery --upgrades`); when a newer build exists it
  offers to install it into the live root's writable overlay and restarts
  the installer with the same arguments.  This lets a fix such as 6-13 be
  picked up from an older ISO instead of rebuilding the media.
- Skip the check in simulation, dry-run and non-live environments, and
  keep the current installer when the check or the update fails.

* Mon Nov 09 2026 tenko <build@tenko.invalid> 6-13
- Force a full curses repaint on every screen, and redraw idle prompts on
  a one-second timer.  The installer runs on the kernel console (tty1),
  so printk messages from mkfs, mount and udev overwrote the header and
  footer.  curses never repainted cells it believed were unchanged, which
  is why the screen stayed corrupt after filesystem creation.  The
  progress pane repaints in full on every step change and at least every
  half second, so console damage heals promptly without flickering on
  every burst of command output.

* Mon Nov 09 2026 tenko <build@tenko.invalid> 6-11
- Run nmtui with LC_ALL=C.UTF-8.  nmtui converts label text from UTF-8 to
  the process locale and turns the row into an empty string when that
  fails, so a Chinese SSID was invisible under the installer's C locale.
- Launch nmtui in a kmscon instance on tty3 so the Noto CJK console stack
  renders the SSID instead of the kernel 8x16 font (issue #50).

* Mon Nov 09 2026 tenko <build@tenko.invalid> 6-10
- Ship the live preset as 45-tenko-live.preset so it sorts before
  50-tenko-console.preset.  Preset files are first-match-wins: the old
  90-tenko-live.preset could not disable kmsconvt@tty1 or the first-boot
  root-password service, which took tty1 and left a login prompt instead
  of the installer.  Disable kmsconvt@tty1 explicitly (issue #50).

* Mon Nov 09 2026 tenko <build@tenko.invalid> 6-9
- Do not exit when the package repository is unreachable.  The curses
  preflight now shows a network screen that lists NetworkManager devices,
  runs nmtui-connect (or nmtui) with curses suspended, and retries the
  repository check; the plain/serial flow offers the same retry and the
  non-interactive failure prints the nmtui hint (issue #50).
- Use one repository probe attempt in the interactive and plain flows so
  the network screen appears promptly instead of after a two-minute wait;
  the unattended flow keeps the longer retry for slow DHCP leases.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-8
- Keep only the ordering against kmsconvt@tty1.service; drop the Conflicts=.
  The live unit's ConditionPathExists is false on an installed system, but
  systemd still enqueues the conflict stop job and that deletes kmscon's
  start job.  Before= keeps the installer on tty1 while it runs.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-7
- Conflict with and start before kmsconvt@tty1.service.  The live root now
  pulls kmscon in through tenko-base-runtime; the installer must keep tty1
  instead of racing the userspace console for it.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-6
- Add a live-initramfs module that finds the installer ISO on a Ventoy data
  partition and loop-mounts it for dmsquash-live.  Ventoy's UEFI chain loader
  boots the ISO's systemd-boot from the El Torito image, so the kernel never
  sees the ISO file and root=live:CDLABEL=TENKO waited forever (issue #49).
  The scan only runs when a VTOYEFI partition is present and is skipped when
  the TENKO label already exists, so CD and dd-written USB boots are
  unchanged.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-5
- Add the admin user to the kvm group as well as wheel, creating kvm if
  the target does not have it.  This gives the installed user access to
  /dev/kvm for QEMU/KVM tests without sudo.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-4
- Install glibc-locales-extra automatically when the selected locale is
  not C, POSIX or C.UTF-8.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-3
- Add guided answer-file v3 import (`mode` + `disk`, filesystem and swap
  choices) with v2 layouts still supported.  Encryption is rejected until
  LUKS support lands; other locales note that locale data is required.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-2
- Add timezone, locale and keymap selection to the guided, plain and
  answer-file flows.  Write /etc/localtime, /etc/locale.conf and
  /etc/vconsole.conf during configure; install tzdb in the target.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-1
- Rebase on the Tenko 6 distro release with Epoch 1 so installs carrying
  the old 13.1 EVR upgrade cleanly.
- Drop the browneye-installer Obsoletes/Provides alias and the old
  payload, unit, preset, dracut and log cleanup; no Browneye installs
  remain.

* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-25
- Rename browneye-installer to tenko-installer and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.
- Use the Tenko 6 (Workstation) distro identity and repository
  (tenko-6.repo, https://tenko.pjfox.xyz/packages/6/) for fresh installs.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-24
- Install OpenSSH and git in every target (desktop and base-only).  They
  are already at the base-set versions (OpenSSH 10.6p1, git 2.56.0).
  The live image is deliberately unaffected: browneye-live builds from
  browneye-base-runtime, which stays minimal.

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
  and swap.  Require btrfs-progs 7.3.
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
