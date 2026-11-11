Name:       adwaita-icon-theme
Version:    51.0
Release:    3
Summary:    Gnome standard icon set.
License:    LGPL-3.0-only OR CC-BY-SA-3.0
URL:        https://gitlab.gnome.org/GNOME/adwaita-icon-theme
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: gtk+


%description
Gnome standard icons.

%prep
%setup

%build
mkdir build
pushd build
meson setup --prefix=/usr ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
# AdwaitaLegacy is not shipped; the Icon Theme spec requires inherited
# themes to be installed.  Fall back to hicolor only (issue #35).
sed -i 's/^Inherits=.*/Inherits=hicolor/' \
    %{buildroot}%{_datadir}/icons/Adwaita/index.theme

%files -f %{_sourcedir}/adwaita-icon-theme.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 51.0-3
- Inherit only hicolor in index.theme.  AdwaitaLegacy is not packaged, and
  the Icon Theme spec requires every explicitly inherited theme to be
  installed (issue #35).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 51.0-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-3.0-only OR CC-BY-SA-3.0): COPYING, COPYING_LGPL and COPYING_CCBYSA3 (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 51.0-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 3.30.1
- Initial RPM release

