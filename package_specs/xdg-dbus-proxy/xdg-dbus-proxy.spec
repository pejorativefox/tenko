Name:       xdg-dbus-proxy
Version:    0.1.9
Release:    1
Summary:    filtering proxy for D-Bus connections
License:    LGPL
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

%files
/usr/bin/xdg-dbus-proxy

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.1.9-1
- Sync with BLFS r13.1

* Thu Sep 10 2020 Chris Statzer <chris.statzer@qq.com> 0.1.2
- Initial RPM

