Name:       atkmm
Version:    2.28.5
Release:    2
Summary:    atkmm is the C++ binding for the ATK library. 
License:    LGPL-2.1-or-later
URL:        https://gitlab.gnome.org/GNOME/atkmm
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: at-spi2-core
BuildRequires: glibmm
BuildRequires: libpeas
BuildRequires: libsigc++

%description
atkmm is the C++ binding for the ATK library. 

%prep
%setup

%build
mkdir build
pushd build
meson setup --prefix=/usr --buildtype=release ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/atkmm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.28.5-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING and the atk/atkmm headers (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.28.5-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2.28.3-1
- Version bump

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 2.28.0-1
- Initial RPM

