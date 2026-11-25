Name:       libtiff
Version:    4.7.2
Release:    1
Summary:    Library for reading and writing TIFF image files
License:    libtiff
URL:        https://libtiff.gitlab.io/libtiff/
Source0:    tiff-%{version}.tar.xz
Prefix:     /usr

BuildRequires: cmake
BuildRequires: gcc
BuildRequires: ninja
BuildRequires: libjpeg-turbo
BuildRequires: libpng
BuildRequires: webp
BuildRequires: xz
BuildRequires: zlib
BuildRequires: zstd

%description
libtiff provides support for reading and writing TIFF (Tagged Image
File Format) files, a widely used format for lossless image storage.
It ships the libtiff runtime library, the tiffcp/tiffinfo command-line
tools, and the headers and pkg-config file that GIMP and other image
toolkits build against.

%prep
%setup -q -n tiff-%{version}

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D CMAKE_BUILD_TYPE=Release \
      -D tiff-docs=OFF \
      -D tiff-tests=OFF \
      -D tiff-contrib=OFF \
      -D tiff-opengl=OFF \
      -D jbig=OFF \
      -D lerc=OFF \
      -D libdeflate=OFF \
      -G Ninja ..
ninja %{?_smp_mflags}
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libtiff.filelist

%changelog
* Wed Nov 25 2026 tenko <build@tenko.invalid> 4.7.2-1
- New package, not in the base set: latest upstream stable release
  (4.7.2, checked 2026-11-25); GIMP's TIFF plug-in links against it.
- JBIG, LERC and libdeflate codecs are disabled (no jbig-kit, liblerc
  or libdeflate packages in the repository); documentation, tests,
  contrib and the OpenGL tiffgt viewer are not built.
