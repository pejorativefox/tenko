Name:       libsigc++
Version:    2.12.1
Release:    2
Summary:    libsigc++ provides a typesafe (at compile time) callback system for standard C++.
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
libsigc++ provides a typesafe (at compile time) callback system for standard C++.

%prep
%setup

%build
sed -i "s/'system',//" meson.build
mkdir bld
pushd bld
meson setup --prefix=/usr --buildtype=release ..
ninja
popd

%install
rm -rf %{buildroot}
pushd bld
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libsigc++.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.12.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING, plus sigc++/*.h "version 2.1 ... or any later version" (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.12.1-1
- Sync with the base set

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 2.10.3
- Initial RPM

