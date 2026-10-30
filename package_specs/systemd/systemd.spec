Name:       systemd
Version:    261.2
Release:    1
Summary:    The systemd package contains programs for controlling the startup, running, and shutdown of the system.
License:    GPL
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

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
      -D pamconfdir=no          \
      -D dev-kvm-mode=0660      \
      -D nobody-group=nogroup   \
      -D sysupdate=disabled     \
      -D ukify=disabled         \
      -D docdir=/usr/share/doc/systemd-%{version}
ninja -j%{_smp_build_ncpus}
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files
/etc/
/usr/bin/
/usr/include/
/usr/lib/
/usr/lib64/
/usr/sbin/
/usr/share/

%changelog
* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 245
- Initial RPM

