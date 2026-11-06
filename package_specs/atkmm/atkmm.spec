Name:       atkmm
Version:    2.28.5
Release:    2
Summary:    atkmm is the C++ binding for the ATK library. 
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

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

%files
/usr/lib64/atkmm-1.6/include/atkmmconfig.h
/usr/lib64/atkmm-1.6/proc/m4/convert.m4
/usr/lib64/atkmm-1.6/proc/m4/convert_atk.m4
/usr/lib64/libatkmm-1.6.so
/usr/lib64/libatkmm-1.6.so.1
/usr/lib64/libatkmm-1.6.so.1.1.0
/usr/lib64/pkgconfig/atkmm-1.6.pc
/usr/include/atkmm-1.6/

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

