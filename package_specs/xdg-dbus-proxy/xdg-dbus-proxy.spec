Name:       xdg-dbus-proxy
Version:    0.1.9
Release:    2
Summary:    filtering proxy for D-Bus connections
License:    LGPL-2.1-or-later AND LGPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
filtering proxy for D-Bus connections

%prep
%setup -q

%build
mkdir build
pushd build
meson setup --prefix=/usr --buildtype=release -Dman=disabled ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/xdg-dbus-proxy.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.1.9-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later AND LGPL-2.0-or-later): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.1.9-1
- Sync with the base set

* Thu Sep 10 2020 Chris Statzer <chris.statzer@qq.com> 0.1.2
- Initial RPM

