Name:       libpoppler
Version:    26.10.0
Release:    1
Summary:    PDF rendering library based on the xpdf-3.0 code base
License:    GPL-2.0-or-later
Source0:    poppler-%{version}.tar.xz
Prefix:     /usr

BuildRequires: cmake, ninja
BuildRequires: openjpeg
BuildRequires: pkgconfig(freetype2)
BuildRequires: pkgconfig(fontconfig)
BuildRequires: pkgconfig(harfbuzz)
BuildRequires: pkgconfig(libjpeg)
BuildRequires: pkgconfig(libpng)
BuildRequires: pkgconfig(cairo)
BuildRequires: pkgconfig(libcurl)
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: gobject-introspection

%description
Poppler is a PDF rendering library based on the xpdf-3.0 code base.
It provides the command-line PDF utilities (pdfinfo, pdftotext,
pdftoppm and others) and the C++, GLib and GObject-Introspection
bindings.

%prep
%setup -q -n poppler-%{version}

%build
mkdir build
pushd build
cmake -G Ninja                          \
      -D CMAKE_BUILD_TYPE=Release       \
      -D CMAKE_INSTALL_PREFIX=/usr      \
      -D CMAKE_INSTALL_LIBDIR=lib64     \
      -D ENABLE_UNSTABLE_API_ABI_HEADERS=ON \
      -D ENABLE_QT5=OFF                 \
      -D ENABLE_QT6=OFF                 \
      -D ENABLE_BOOST=OFF               \
      -D ENABLE_LCMS=OFF                \
      -D ENABLE_LIBTIFF=OFF             \
      -D ENABLE_NSS3=OFF                \
      -D ENABLE_GPGME=OFF               \
      -D ENABLE_BROTLI=OFF              \
      ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libpoppler.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 26.10.0-1
- Update to 26.10.0, the version in the BLFS r13.1 book
  (general/graphlib/poppler.xml).
- Follow the book's Ninja/CMake build and keep
  ENABLE_UNSTABLE_API_ABI_HEADERS=ON.
- Enable the dependencies this repository ships: libjpeg-turbo,
  libpng, freetype, fontconfig, harfbuzz, openjpeg, curl, cairo,
  glib and GObject-Introspection (plus zlib and brotli-free streams).
- Disable what is neither in the book build nor in the repository:
  lcms2, libtiff, nss, gpgme, boost, qt5 and qt6, and brotli (not
  installed in the build image; poppler's CMake would otherwise
  abort).
- Install to /usr/lib64 explicitly (CMake's /usr-prefix default is
  lib); no -devel subpackage, as usual.
