Name:       systemd
Version:    261.3
Release:    3
Summary:    The systemd package contains programs for controlling the startup, running, and shutdown of the system.
License:    GPL
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: linux-pam
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
      -D nobody-group=nogroup   \
      -D sysupdate=disabled     \
      -D ukify=disabled         \
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

%files -f %{_sourcedir}/systemd.filelist
%files hwdb -f %{_sourcedir}/systemd-hwdb.filelist
%files lang -f %{_sourcedir}/systemd-lang.filelist
%files doc -f %{_sourcedir}/systemd-doc.filelist

%changelog
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

