Name:       babl
Version:    0.1.128
Release:    1
Summary:    Dynamic pixel-format translation library
License:    LGPL-3.0-or-later
URL:        https://gegl.org/babl/
Source0:    babl-%{version}.tar.xz
Prefix:     /usr

BuildRequires: glib
BuildRequires: gobject-introspection
BuildRequires: lcms2

%description
babl is a dynamic library that converts between image formats and
color models, providing a vocabulary to describe pixel buffers and
the fish to translate between them.  GEGL and GIMP pass image data
between operations through it; GIMP 3 in addition loads its color
spaces through the GObject introspection typelib.

%package gir
Summary:    GObject Introspection data for babl
License:    LGPL-3.0-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for babl, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                     \
      --prefix=/usr                \
      --buildtype=release          \
      -D enable-gir=true           \
      -D enable-vapi=false         \
      -D with-docs=false           \
      -D gi-docgen=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/babl.filelist
%files gir -f %{_sourcedir}/babl-gir.filelist

%changelog
* Wed Nov 25 2026 tenko <build@tenko.invalid> 0.1.128-1
- New package, not in the base set: latest upstream stable release
  (0.1.128, checked 2026-11-25); GIMP 3 needs typelib(Babl).
- GObject introspection is enabled (enable-gir=true); the vapi file
  and the gi-docgen reference are not built.  lcms2 support is kept
  by declaring it as a build dependency.
