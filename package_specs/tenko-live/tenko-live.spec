Name:       tenko-live
Version:    6
Release:    3
Epoch:      1
Summary:    Tenko Linux 6 (Workstation) live installer environment (meta-package)
License:    MIT
URL:        https://pjfox.xyz/git/daspork/tenko
BuildArch:  noarch
Prefix:     /usr

# The complete live root, not just the runtime base.  This is a meta-package:
# it installs no files of its own, only the closure needed to boot the live
# ISO and run tenko-installer.
Requires:   tenko-base-runtime
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
# The installer is network-only and most Wi-Fi cards need their vendor
# firmware before a wlan interface appears.  build_iso_uefi.sh installs with
# install_weak_deps=False, so these must be real Requires, not Recommends.
Requires:   linux-firmware-intel-wifi
Requires:   linux-firmware-ath
Requires:   linux-firmware-mediatek
Requires:   linux-firmware-other
Requires:   linux-firmware-nic
Requires:   python
Requires:   ncurses
Requires:   util-linux
Requires:   e2fsprogs
Requires:   btrfs-progs
Requires:   tzdb
Requires:   tenko-installer

%description
Meta-package for the Tenko Linux 6 (Workstation) live installation environment.

It pulls in the runtime base, the kernel and modules, firmware, dnf,
dracut, dosfstools, efibootmgr/efivar, LVM2 (for dmsetup, which
dracut's live modules require), Python, ncurses, util-linux, e2fsprogs,
btrfs-progs and tenko-installer.  It ships no files; tenko-installer
owns the unit,
the live systemd preset and the dracut dmsquash-live configuration.

It also pulls the vendor Wi-Fi and NIC firmware packs, because the
installer downloads every package and most wireless cards need external
firmware before NetworkManager can offer an interface.

%prep

%build

%install

%files

%changelog
* Mon Nov 09 2026 tenko <build@tenko.invalid> 6-3
- Require the vendor Wi-Fi and NIC firmware packs (Intel, Atheros,
  MediaTek, Realtek wired and the remaining Broadcom/Cypress/etc. blobs).
  The live kernel already ships iwlwifi/ath/rtw*/mt76 drivers, but the
  media only carried linux-firmware-base, so a wireless card was detected
  and then failed to load firmware, leaving the network-only installer
  with no usable interface (issue #50).

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-2
- Require tzdb: the live environment needs zoneinfo for the installer's
  timezone selection and validation.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-1
- Rebase on the Tenko 6 distro release with Epoch 1 so installs carrying
  the old 13.1 EVR upgrade cleanly.
- Drop the browneye-live Obsoletes/Provides alias; no Browneye installs
  remain.

* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-4
- Rename browneye-live to tenko-live and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-3
- Require btrfs-progs 7.3 so the live installer can create
  btrfs root and data filesystems.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 13.1-2
- Drop the grub requirement: the live environment and the installer now use
  systemd-boot from the systemd package (docs/systemd-boot.md).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-1
- New meta-package for the UEFI-only live installer: base-runtime, dnf,
  grub, dracut, dosfstools, efibootmgr/efivar, LVM2 (dmsetup for
  dmsquash-live), kernel/modules/firmware, Python/ncurses and the
  browneye-installer application.
