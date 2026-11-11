Name:       cairomm
Version:    1.14.6
Release:    2
Summary:    The Cairomm package provides a C++ interface to Cairo. 
License:    LGPL-2.1-or-later
URL:        https://www.cairographics.org/cairomm/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: libsigc++
BuildRequires: cairo

%description
The Cairomm package provides a C++ interface to Cairo. 

%prep
%setup

%build
mkdir bld
pushd bld
meson setup ..             \
      --prefix=/usr        \
      --buildtype=release  \
      -D build-tests=false  \
      -D boost-shared=true
ninja
popd

%install
rm -rf %{buildroot}
pushd bld
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/cairomm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.14.6-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING and the cairomm/ headers (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.14.6-1
- Sync with the base set

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 1.12.2
- Initial RPM

