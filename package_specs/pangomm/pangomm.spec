Name:       pangomm
Version:    2.46.5
Release:    2
Summary:    pangomm is the official C++ interface for the Pango font layout library. 
License:    LGPL-2.1-or-later
URL:        https://gitlab.gnome.org/GNOME/pangomm
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: glibmm
BuildRequires: cairomm
BuildRequires: libsigc++
BuildRequires: pango

%description
pangomm is the official C++ interface for the Pango font layout library. 

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

%files -f %{_sourcedir}/pangomm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.46.5-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.46.5-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2.46.3-1
- Version bump

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 2.42.1
- Initial RPM

