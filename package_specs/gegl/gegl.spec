Name:       gegl
Version:    0.4.72
Release:    1
Summary:    Graph-based image processing framework
License:    LGPL-3.0-or-later AND GPL-3.0-or-later
URL:        https://www.gegl.org/
Prefix:     /usr
Source0:    gegl-%{version}.tar.xz

BuildRequires: babl
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: gexiv2
BuildRequires: glib
BuildRequires: gobject-introspection
BuildRequires: json-glib
BuildRequires: lcms2
BuildRequires: libjpeg-turbo
BuildRequires: libpng
BuildRequires: libpoppler
BuildRequires: librsvg
BuildRequires: libtiff
BuildRequires: pango
BuildRequires: python3-gobject
BuildRequires: sdl2
BuildRequires: webp

%description
GEGL (Generic Graphics Library) is a graph-based image processing
framework providing floating point processing and non-destructive
image editing.  It is the pixel-processing core used by GIMP; the
library is LGPL while the gegl(1) tool and some operations are GPL.

%package lang
Summary:    gegl translations
Requires:   gegl = %{version}-%{release}

%description lang
Translations for gegl.

%package gir
Summary:    GObject Introspection data for gegl
License:    LGPL-3.0-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for gegl, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%prep
%setup -q -n gegl-%{version}

%build
mkdir build
pushd build
meson setup ..                        \
      --prefix=/usr                   \
      --buildtype=release             \
      -D docs=false                   \
      -D gi-docgen=disabled           \
      -D introspection=true           \
      -D vapigen=disabled             \
      -D workshop=false               \
      -D operation-test=false         \
      -D libav=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/gegl.filelist
%files lang -f %{_sourcedir}/gegl-lang.filelist
%files gir -f %{_sourcedir}/gegl-gir.filelist

%changelog
* Wed Nov 25 2026 tenko <build@tenko.invalid> 0.4.72-1
- New package, not in the base set: latest upstream stable release
  (0.4.72, checked 2026-11-25), the GEGL release accompanying GIMP 3.2
  (GIMP 3.2.8 requires gegl >= 0.4.66).
- Optional operations without a packaged dependency are disabled at
  build time: openexr, libraw, lensfun, jasper, libspiro, maxflow,
  umfpack, libv4l, graphviz, mrg and luajit are not in the repository.
- Introspection data is split into the -gir subpackage; the .gir XML
  stays in the main package for building against gegl.
