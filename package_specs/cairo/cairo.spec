Name:       cairo
Version:    1.18.6
Release:    5
Summary:    2D graphics library
License:    LGPL-2.1-only OR MPL-1.1
URL:        https://www.cairographics.org/
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: pkgconfig(freetype2)
BuildRequires: pkgconfig(xext)
BuildRequires: pkgconfig(xcb-render)
BuildRequires: pkgconfig(xrender)
BuildRequires: fontconfig
BuildRequires: gobject-introspection
BuildRequires: liblzo2
BuildRequires: libpng
BuildRequires: libpoppler
BuildRequires: librsvg
BuildRequires: libx11
BuildRequires: pixman
BuildRequires: xorgproto

%description
Cairo is a 2D graphics library with support for multiple output devices.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/cairo.filelist
%changelog
* Wed Nov 25 2026 tenko <build@tenko.invalid> 1.18.6-5
- Build with gobject-introspection and ship the Cairo-1.0 gir and
  typelib: no package in the repository provided the namespace, and
  GIMP's Python bindings (gi.repository import Gimp, used by its
  build-time splash generation and user scripts) cannot load
  without it.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.18.6-4
- Record the verified license (LGPL-2.1-only OR MPL-1.1): COPYING and src/cairo.c (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.18.6-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.18.6-2
- Split devel payload into cairo-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.18.4
- Sync with 1.17.6

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.17.6-1
- Version bump
