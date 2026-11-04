Name:       browneye-live
Version:    13.1
Release:    2
Summary:    Browneye Linux 13.1 live installer environment (meta-package)
License:    MIT
BuildArch:  noarch
Prefix:     /usr

# The complete live root, not just the runtime base.  This is a meta-package:
# it installs no files of its own, only the closure needed to boot the live
# ISO and run browneye-installer.
Requires:   browneye-base-runtime
Requires:   dnf
Requires:   dracut
Requires:   dosfstools
Requires:   efibootmgr
Requires:   efivar
# Package name is upper-case in package_specs/lvm2/lvm2.spec.  lvm2 provides
# dmsetup, which dracut's 70dm/70dmsquash-live modules require.
Requires:   LVM2
Requires:   linux-kernel
Requires:   linux-modules
Requires:   linux-firmware-base
Requires:   python
Requires:   ncurses
Requires:   util-linux
Requires:   e2fsprogs
Requires:   browneye-installer

%description
Meta-package for the Browneye Linux 13.1 live installation environment.

It pulls in the runtime base, the kernel and modules, firmware, dnf,
dracut, dosfstools, efibootmgr/efivar, LVM2 (for dmsetup, which
dracut's live modules require), Python, ncurses, util-linux, e2fsprogs and
browneye-installer.  It ships no files; browneye-installer owns the unit,
the live systemd preset and the dracut dmsquash-live configuration.

%prep

%build

%install

%files

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 13.1-2
- Drop the grub requirement: the live environment and the installer now use
  systemd-boot from the systemd package (docs/systemd-boot.md).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-1
- New meta-package for the UEFI-only live installer: base-runtime, dnf,
  grub, dracut, dosfstools, efibootmgr/efivar, LVM2 (dmsetup for
  dmsquash-live), kernel/modules/firmware, Python/ncurses and the
  browneye-installer application.
