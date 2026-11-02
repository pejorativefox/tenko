Name:       browneye-installer
Version:    13.1
Release:    6
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
Requires:   dnf
Requires:   grub
Requires:   dracut
Requires:   efibootmgr
Requires:   efivar
Requires:   coreutils
Requires:   systemd

%description
A Python 3 / ncurses installer for Browneye Linux 13.1.

It is UEFI-only and GPT-only.  It selects one GPT disk, optionally deletes
selected partition entries, and installs into one contiguous free region
while preserving every other partition.  An existing ESP is reused;
otherwise a 512 MiB FAT32 ESP is created.  Root is ext4 (minimum 8 GiB,
growing to fill the region); swap is 2 GiB when it fits.  The target is
browneye-base + xfce-desktop + kernel/modules + dracut/grub/efibootmgr/
dosfstools/dnf, installed with dnf --installroot after browneye-basefs.

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

for module in log.py runner.py disk.py probe.py install.py ui.py main.py; do
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
