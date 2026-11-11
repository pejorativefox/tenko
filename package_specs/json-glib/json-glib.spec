Name:       json-glib
Version:    1.10.8
Release:    2
Summary:    Glib json support.
License:    LGPL-2.1-or-later
URL:        https://gitlab.gnome.org/GNOME/json-glib
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: gobject-introspection

%description
Glib json support.

%prep
%setup

%build
mkdir build
pushd build
meson --prefix=/usr ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/json-glib.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.10.8-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): meson.build "license: LGPL-2.1-or-later" and the LICENSES/ directory (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.10.8-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.4.2
- Initial RPM

