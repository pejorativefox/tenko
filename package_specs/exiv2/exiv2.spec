Name:       exiv2
Version:    0.28.9
Release:    1
Summary:    Exif, IPTC and XMP metadata library and command-line tool
License:    GPL-2.0-or-later
URL:        https://exiv2.org/
Source0:    exiv2-%{version}.tar.gz
Prefix:     /usr

BuildRequires: brotli
BuildRequires: cmake
BuildRequires: expat
BuildRequires: gcc
BuildRequires: ninja
BuildRequires: zlib

%description
Exiv2 is a C++ library and command-line utility to read, write,
delete and modify Exif, IPTC, XMP and ICC image metadata.  gexiv2,
and through it GIMP, uses it to exchange metadata with image files;
the exiv2 command prints and edits metadata from scripts.

%prep
%setup -q

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D CMAKE_BUILD_TYPE=Release \
      -D EXIV2_ENABLE_VIDEO=OFF \
      -D EXIV2_ENABLE_WEBREADY=OFF \
      -D EXIV2_ENABLE_NLS=OFF \
      -D EXIV2_ENABLE_INIH=OFF \
      -D EXIV2_BUILD_SAMPLES=OFF \
      -D EXIV2_BUILD_UNIT_TESTS=OFF \
      -G Ninja ..
ninja %{?_smp_mflags}
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/exiv2.filelist

%changelog
* Wed Nov 25 2026 tenko <build@tenko.invalid> 0.28.9-1
- New package, not in the base set: latest upstream stable release
  (0.28.9, checked 2026-11-25); gexiv2 and GIMP read and write image
  metadata through it.
- Video and webready support, NLS, the sample applications and unit
  tests are disabled (ffmpeg and curl are not build inputs here);
  inih support is off because the repository ships no inih package
  and exiv2's CMake fails hard without it.  The exiv2 command-line
  tool is kept, and brotli stays enabled for JPEG XL boxes (BMFF).
