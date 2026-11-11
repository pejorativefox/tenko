Name:       glibmm
Version:    2.66.10
Release:    2
Summary:    glibmm is the official C++ interface for the popular cross-platform library Glib. 
License:    LGPL-2.1-or-later
URL:        https://gitlab.gnome.org/GNOME/glibmm
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: libsigc++
BuildRequires: xml-parser

%description
glibmm is the official C++ interface for the popular cross-platform library Glib. 

%prep
%setup

%build
mkdir glibmm-build
pushd glibmm-build
meson setup --prefix=/usr --buildtype=release ..
ninja
popd

%install
rm -rf %{buildroot}
pushd glibmm-build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/glibmm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.66.10-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING and the glib/ and gio/ headers (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.66.10-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2.66.5-1
- Version bump

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 2.58.1
- Initial RPM

