Name:       cairomm
Version:    1.14.6
Release:    2
Summary:    The Cairomm package provides a C++ interface to Cairo. 
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: libsigc++

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

%files
/usr/include/cairomm-1.0/cairomm/cairomm.h
/usr/include/cairomm-1.0/cairomm/context.h
/usr/include/cairomm-1.0/cairomm/device.h
/usr/include/cairomm-1.0/cairomm/enums.h
/usr/include/cairomm-1.0/cairomm/exception.h
/usr/include/cairomm-1.0/cairomm/fontface.h
/usr/include/cairomm-1.0/cairomm/fontoptions.h
/usr/include/cairomm-1.0/cairomm/matrix.h
/usr/include/cairomm-1.0/cairomm/path.h
/usr/include/cairomm-1.0/cairomm/pattern.h
/usr/include/cairomm-1.0/cairomm/quartz_font.h
/usr/include/cairomm-1.0/cairomm/quartz_surface.h
/usr/include/cairomm-1.0/cairomm/refptr.h
/usr/include/cairomm-1.0/cairomm/region.h
/usr/include/cairomm-1.0/cairomm/scaledfont.h
/usr/include/cairomm-1.0/cairomm/script.h
/usr/include/cairomm-1.0/cairomm/script_surface.h
/usr/include/cairomm-1.0/cairomm/surface.h
/usr/include/cairomm-1.0/cairomm/types.h
/usr/include/cairomm-1.0/cairomm/win32_font.h
/usr/include/cairomm-1.0/cairomm/win32_surface.h
/usr/include/cairomm-1.0/cairomm/xlib_surface.h
/usr/lib64/cairomm-1.0/include/cairommconfig.h
/usr/lib64/libcairomm-1.0.so
/usr/lib64/libcairomm-1.0.so.1
/usr/lib64/libcairomm-1.0.so.1.4.0
/usr/lib64/pkgconfig/cairomm-1.0.pc
/usr/lib64/pkgconfig/cairomm-ft-1.0.pc
/usr/lib64/pkgconfig/cairomm-pdf-1.0.pc
/usr/lib64/pkgconfig/cairomm-png-1.0.pc
/usr/lib64/pkgconfig/cairomm-ps-1.0.pc
/usr/lib64/pkgconfig/cairomm-svg-1.0.pc
/usr/lib64/pkgconfig/cairomm-xlib-1.0.pc
/usr/lib64/pkgconfig/cairomm-xlib-xrender-1.0.pc

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.14.6-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING and the cairomm/ headers (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.14.6-1
- Sync with the base set

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 1.12.2
- Initial RPM

