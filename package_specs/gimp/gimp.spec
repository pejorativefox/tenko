Name:       gimp
Version:    3.2.8
Release:    1
Summary:    GNU Image Manipulation Program
License:    GPL-3.0-or-later AND LGPL-3.0-or-later
URL:        https://www.gimp.org/
Prefix:     /usr
Source0:    gimp-%{version}.tar.xz

BuildRequires: alsa-lib
BuildRequires: appstream
BuildRequires: at-spi2-core
BuildRequires: babl
BuildRequires: bash-completion
BuildRequires: bzip2
BuildRequires: cairo
BuildRequires: exiv2
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: fribidi
BuildRequires: gdk-pixbuf
BuildRequires: gegl
BuildRequires: gexiv2
BuildRequires: glib
BuildRequires: glib-networking
BuildRequires: gobject-introspection
BuildRequires: gtk+
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
BuildRequires: poppler-data
BuildRequires: python
BuildRequires: python3-gobject
BuildRequires: python3-pycairo
BuildRequires: shared-mime-info
BuildRequires: webp
BuildRequires: xz
BuildRequires: zlib

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

%package gir
Summary:    GObject Introspection data for gimp
License:    LGPL-3.0-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for the Gimp and GimpUi libraries,
split out of the runtime package so a plain install does not carry
the introspection data.  The .gir XML needed for building stays in
the main package.

%prep
%setup -q -n gimp-%{version}

%build
mkdir build
pushd build
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
      -D pdf=enabled                  \
      -D webp=enabled                \
      -D wmf=disabled                \
      -D xcursor=enabled              \
      -D xpm=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/gimp.filelist
%files lang -f %{_sourcedir}/gimp-lang.filelist
%files gir -f %{_sourcedir}/gimp-gir.filelist

%changelog
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
