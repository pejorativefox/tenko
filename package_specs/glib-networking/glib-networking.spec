Name:       glib-networking
Version:    2.90.1
Release:    2
Summary:    Network related gio modules for GLib. 
License:    LGPL-2.1-or-later
URL:        https://gitlab.gnome.org/GNOME/glib-networking
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: gsettings-desktop-schemas
BuildRequires: gnutls

%description
Network related gio modules for GLib. 

%prep
%setup

%build
mkdir build
pushd build
meson setup --prefix=/usr --buildtype=release -D libproxy=disabled ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/glib-networking.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.90.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING, LICENSE_EXCEPTION and tls/base/gtlslog.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.90.1-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 2.56.1
- Initial RPM

