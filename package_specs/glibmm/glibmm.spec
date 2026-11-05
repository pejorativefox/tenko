Name:       glibmm
Version:    2.66.10
Release:    2
Summary:    glibmm is the official C++ interface for the popular cross-platform library Glib. 
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

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

%files
/usr/include/giomm-2.4/
/usr/include/glibmm-2.4/
/usr/lib64/giomm-2.4/
/usr/lib64/glibmm-2.4/
/usr/lib64/libgiomm-2.4.so
/usr/lib64/libgiomm-2.4.so.1
/usr/lib64/libgiomm-2.4.so.1.3.0
/usr/lib64/libglibmm-2.4.so
/usr/lib64/libglibmm-2.4.so.1
/usr/lib64/libglibmm-2.4.so.1.3.0
/usr/lib64/libglibmm_generate_extra_defs-2.4.so
/usr/lib64/libglibmm_generate_extra_defs-2.4.so.1
/usr/lib64/libglibmm_generate_extra_defs-2.4.so.1.3.0
/usr/lib64/pkgconfig/giomm-2.4.pc
/usr/lib64/pkgconfig/glibmm-2.4.pc

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.66.10-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING and the glib/ and gio/ headers (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.66.10-1
- Sync with BLFS r13.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2.66.5-1
- Version bump

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 2.58.1
- Initial RPM

