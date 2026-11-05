Name:       systemd
Version:    262.1
Release:    4
Summary:    The systemd package contains programs for controlling the startup, running, and shutdown of the system.
License:    LGPL-2.1-or-later AND GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: linux-pam
BuildRequires: python3-pyelftools
Requires: linux-pam
# The hardware database is only useful on real hardware.  Containers and
# other minimal installs can omit it (dnf --setopt=install_weak_deps=False)
# while desktop installs still get it by default.
Recommends: systemd-hwdb = %{version}-%{release}

%description
The systemd package contains programs for controlling the startup, running, and shutdown of the system.

%package hwdb
Summary:    udev hardware database and systemd-hwdb
Requires:   systemd = %{version}-%{release}

%description hwdb
The udev hardware database (hwdb.d) and the systemd-hwdb tool that compiles
it.  systemd and udev work without this package; hardware-specific properties
are then simply unavailable.

%package lang
Summary:    systemd translations

%description lang
Translations of the systemd programs and messages.

%package doc
Summary:    systemd documentation

%description doc
README, NEWS, licence texts and, when built with man pages enabled, the
systemd manual pages.

%prep
%setup

%build
mkdir -p build
pushd build
meson setup ..                  \
      --prefix=/usr             \
      --buildtype=release       \
      -D default-dnssec=no      \
      -D firstboot=false        \
      -D install-tests=false    \
      -D ldconfig=false         \
      -D sysusers=true         \
      -D rpmmacrosdir=no        \
      -D homed=disabled         \
      -D man=disabled           \
      -D mode=release           \
      -D pam=true               \
      -D pamconfdir=/etc/pam.d  \
      -D dev-kvm-mode=0660      \
      -D swapon-path=/usr/bin/swapon   \
      -D swapoff-path=/usr/bin/swapoff \
      -D nobody-group=nogroup   \
      -D sysupdate=disabled     \
      -D ukify=disabled         \
      -D bootloader=enabled     \
      -D sbat-distro-url=https://pjfox.xyz/git/daspork/browneye/issues \
      -D importd=disabled      \
      -D remote=disabled       \
      -D imds=disabled         \
      -D docdir=/usr/share/doc/systemd-%{version}
ninja -j%{_smp_build_ncpus}
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

# -D bootloader=enabled is only honoured when python3-pyelftools is present;
# meson otherwise disables ENABLE_BOOTLOADER silently.  Fail loudly instead of
# shipping a systemd without sd-boot.
test -f %{buildroot}/usr/lib/systemd/boot/efi/systemd-bootx64.efi || {
    echo "systemd-bootx64.efi was not built; install python3-pyelftools" >&2
    exit 1
}

%files -f %{_sourcedir}/systemd.filelist
%files hwdb -f %{_sourcedir}/systemd-hwdb.filelist
%files lang -f %{_sourcedir}/systemd-lang.filelist
%files doc -f %{_sourcedir}/systemd-doc.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 262.1-4
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later AND GPL-2.0-or-later): LICENSES/README.md (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 262.1-3
- Build the EFI bootloader: -D bootloader=enabled with the new
  python3-pyelftools build dependency.  meson requires the Python elftools
  module for ENABLE_BOOTLOADER and silently skips sd-boot and the EFI stub
  without it, which is why 262.1-1/-2 shipped bootctl but no
  /usr/lib/systemd/boot/efi/systemd-bootx64.efi.  First step of the
  systemd-boot conversion (docs/systemd-boot.md); ukify stays disabled, so
  python-pefile is still not needed.
- Assert in %%install that systemd-bootx64.efi was produced so a future
  build without pyelftools fails instead of regressing.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 262.1-2
- Build with -Dswapon-path=/usr/bin/swapon and
  -Dswapoff-path=/usr/bin/swapoff.  The distro maps sbindir to /usr/bin
  (util-linux installs swapon there), but systemd's default is
  /usr/sbin/swapon, so activating the installer's swap partition failed
  at boot with "Failed at step EXEC spawning /usr/sbin/swapon".  Found by
  the unattended installer test.

* Mon Nov  2 2026 browneye <build@browneye.invalid> 262.1-1
- Update to 262.1 (current LFS/BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 261.3-3
- Bump the release for the hwdb/lang/doc split: the 261.3-2 build is
  already published with the old monolithic payload, so the split needs
  a new NEVR for upgrades to install it

* Sun Nov 01 2026 browneye <build@browneye.invalid> 261.3-2
- Split systemd-hwdb (hwdb.d, hwdb binary, update service and shell
  completions), systemd-lang and systemd-doc out of the main package.
  systemd Recommends systemd-hwdb so containers can omit it
- Rebuild with Linux-PAM: -D pam=true and -D pamconfdir=/etc/pam.d
  (installs pam_systemd.so, systemd-user PAM config, and
  systemd-user-sessions.service); fix Source0 to the 261.3 tarball

* Sat Oct 31 2026 browneye <build@browneye.invalid> 261.2
- Replace directory globs with a generated static filelist

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 245
- Initial RPM

