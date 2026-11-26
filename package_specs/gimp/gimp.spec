Name:       gimp
Version:    3.2.8
Release:    2
Summary:    GNU Image Manipulation Program
License:    GPL-3.0-or-later AND LGPL-3.0-or-later
URL:        https://www.gimp.org/
Prefix:     /usr
Source0:    gimp-%{version}.tar.xz
Obsoletes:  gimp-gir < %{version}-%{release}
Provides:   gimp-gir = %{version}-%{release}

BuildRequires: alsa-lib
BuildRequires: appstream
BuildRequires: at-spi2-core
BuildRequires: at-spi2-core-gir
BuildRequires: babl
BuildRequires: babl-gir
BuildRequires: bash-completion
BuildRequires: bzip2
BuildRequires: cairo
BuildRequires: exiv2
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: fribidi
BuildRequires: gdk-pixbuf
BuildRequires: gdk-pixbuf-gir
BuildRequires: gegl
BuildRequires: gegl-gir
BuildRequires: gexiv2
BuildRequires: glib
BuildRequires: glib-networking
BuildRequires: gobject-introspection
BuildRequires: gobject-introspection-gir
BuildRequires: gtk+
BuildRequires: gtk+-gir
BuildRequires: harfbuzz-gir
BuildRequires: harfbuzz
BuildRequires: iso-codes
BuildRequires: json-glib
BuildRequires: lcms2
BuildRequires: libarchive
BuildRequires: libgudev
BuildRequires: libjpeg-turbo
BuildRequires: libmypaint
BuildRequires: libpng
BuildRequires: libpoppler
BuildRequires: librsvg
BuildRequires: libtiff
BuildRequires: libx11
BuildRequires: libxcursor
BuildRequires: libxext
BuildRequires: libxfixes
BuildRequires: libxmu
BuildRequires: mypaint-brushes
BuildRequires: openjpeg
BuildRequires: pango
BuildRequires: pango-gir
BuildRequires: poppler-data
BuildRequires: python
BuildRequires: python3-gobject
BuildRequires: python3-pycairo
BuildRequires: shared-mime-info
BuildRequires: webp
BuildRequires: xz
BuildRequires: libxslt
BuildRequires: zlib

# GIMP shells out to xdg-email for the Send-to command, and the shipped
# Python plug-ins import gi (Babl, Gegl, Gimp) and cairo at runtime.
# The Gimp/GimpUi typelibs ship in this package: the Python plug-ins load
# them, so they are not optional.
Requires:   babl-gir
Requires:   at-spi2-core-gir
Requires:   gegl-gir
Requires:   gobject-introspection-gir
Requires:   gtk+-gir
Requires:   harfbuzz-gir
Requires:   pango-gir
Requires:   gdk-pixbuf-gir
Requires:   python3-gobject
Requires:   python3-pycairo
Requires:   xdg-utils

%description
GIMP (GNU Image Manipulation Program) is a raster image editor for
photo retouching, image composition and authoring.  It provides a
layered workflow with a plug-in API for C and Python (PyGObject)
extensions and a Script-Fu console.  The core is GPL-3.0-or-later;
the libgimp plug-in libraries are LGPL-3.0-or-later.

%package lang
Summary:    gimp translations
Requires:   gimp = %{version}-%{release}

%description lang
Translations for gimp.

%prep
%setup -q -n gimp-%{version}

%build
# The source tree ships its own build/ directory, so use another name.
mkdir build-dir
pushd build-dir
meson setup ..                        \
      --prefix=/usr                   \
      --buildtype=release             \
      -D check-update=no              \
      -D appdata-test=disabled        \
      -D gi-docgen=disabled           \
      -D headless-tests=disabled      \
      -D javascript=disabled          \
      -D lua=false                    \
      -D vala=disabled                \
      -D webkit-unmaintained=false    \
      -D aa=disabled                  \
      -D cairo-pdf=enabled            \
      -D fits=disabled                \
      -D ghostscript=disabled         \
      -D gudev=enabled                \
      -D heif=disabled                \
      -D jpeg-xl=disabled            \
      -D jpeg2000=enabled            \
      -D mng=disabled                \
      -D openexr=disabled             \
      -D webp=enabled                \
      -D wmf=disabled                \
      -D xcursor=enabled              \
      -D xpm=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build-dir
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/gimp.filelist
%files lang -f %{_sourcedir}/gimp-lang.filelist

%changelog
* Thu Nov 26 2026 tenko <build@tenko.invalid> 3.2.8-2
- Fold gimp-gir back into gimp: the Gimp-3.0 and GimpUi-3.0
  typelibs return to the runtime package, so the shipped Python
  plug-ins work on a plain install without a separate gimp-gir
  install.  The subpackage's premise, that introspection data is
  optional, does not hold when the plug-ins that load it are in the
  main package.
  gimp obsoletes gimp-gir < 3.2.8-2 and provides gimp-gir = 3.2.8-2,
  so an upgrade replaces the published 3.2.8-1 gimp-gir (which
  Requires gimp = 3.2.8-1) instead of keeping both.

* Wed Nov 25 2026 tenko <build@tenko.invalid> 3.2.8-1
- New package, not in the base set: latest upstream stable release
  (3.2.8, checked 2026-11-25), built with babl 0.1.128 and gegl 0.4.72.
- Python scripting (PyGObject), JPEG 2000 (openjpeg), WebP, PDF
  (poppler), cairo PDF export, ALSA MIDI input and xcursor file
  support are enabled.
- Importers and features whose optional dependencies are not yet
  packaged are disabled: HEIF, JPEG XL, OpenEXR, MNG, WMF, FITS,
  Ghostscript, aalib and XPM (libXpm); the unmaintained WebKit help
  browser and the experimental Lua and JavaScript bindings stay off.
- Introspection data is split into the -gir subpackage; the .gir XML
  stays in the main package for building plug-ins against gimp.
