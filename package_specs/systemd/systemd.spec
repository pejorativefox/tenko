Name:       systemd
Version:    261.3
Release:    2
Summary:    The systemd package contains programs for controlling the startup, running, and shutdown of the system.
License:    GPL
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: linux-pam
Requires: linux-pam

%description
The systemd package contains programs for controlling the startup, running, and shutdown of the system.

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

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 261.3-2
- Rebuild with Linux-PAM: -D pam=true and -D pamconfdir=/etc/pam.d
  (installs pam_systemd.so, systemd-user PAM config, and
  systemd-user-sessions.service); fix Source0 to the 261.3 tarball

* Sat Oct 31 2026 browneye <build@browneye.invalid> 261.2
- Replace directory globs with a generated static filelist

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 245
- Initial RPM

