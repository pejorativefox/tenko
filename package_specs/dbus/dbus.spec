%global _python_bytecompile_errors_terminate_build 0

Name:       dbus
Version:    1.16.2
Release:    2
Summary:    D-BUS message bus
License:    AFL-2.1 OR GPL-2.0-or-later
URL:        https://gitlab.freedesktop.org/dbus/dbus
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
D-BUS is a system for sending messages between applications.

%prep
%setup

%build
mkdir -p build
pushd build
meson setup --prefix=/usr --buildtype=release --wrap-mode=nofallback -D selinux=disabled ..
ninja -j%{_smp_build_ncpus}
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*
sed -i 's|#!/usr/bin/env python$|#!/usr/bin/env python3|' %{buildroot}/usr/share/doc/dbus/examples/GetAllMatchRules.py

%post
mkdir -pv /var/lib/dbus
mkdir -pv /run/dbus
useradd -c "D-Bus Message Daemon User" -d /var/run/dbus \
        -u 18 -g messagebus -s /bin/false messagebus
chown -v root:messagebus /usr/libexec/dbus-daemon-launch-helper &&
chmod -v      4750       /usr/libexec/dbus-daemon-launch-helper
dbus-uuidgen --ensure

%package daemon
Summary:        D-BUS message bus
%description daemon
The DBUS daemon

%files daemon -f %{_sourcedir}/dbus-daemon.filelist

%package x11
Summary:  x11 addons for D-BUS
%description x11
D-BUS contains some tools that require Xlib to be installed

%files x11 -f %{_sourcedir}/dbus-x11.filelist

%package libs
Summary: D-BUS libraries
%description libs
This package contains libraries for accessing D-BUS.

%files libs -f %{_sourcedir}/dbus-libs.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.16.2-2
- Record the verified license (AFL-2.1 OR GPL-2.0-or-later): COPYING (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.16.2
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.14.8-1
- Version bump

* Thu May 15 2020 Chris Statzer <chris.statzer@qq.com> 1.12.12
- Split up the dbus components into seperate packages isolating the
  X11 and lib components.

