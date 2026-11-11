Name:       openjpeg
Version:    2.5.4
Release:    1
Summary:    An open-source JPEG 2000 codec written in C
License:    BSD-2-Clause
URL:        https://www.openjpeg.org/
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

BuildRequires: cmake
BuildRequires: libpng

%description
OpenJPEG is an open-source JPEG 2000 codec written in C.  It can
compress and decompress lossless 16-bit images and is used by Poppler
for JPX streams.

%prep
%setup -q

%build
mkdir build
pushd build
cmake -D CMAKE_BUILD_TYPE=Release    \
      -D CMAKE_INSTALL_PREFIX=/usr  \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D BUILD_STATIC_LIBS=OFF      \
      ..
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
%make_install
popd
install -d %{buildroot}/usr/share/man
cp -rv doc/man/. -T %{buildroot}/usr/share/man

%files -f %{_sourcedir}/openjpeg.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.5.4-1
- Update to 2.5.4, the pinned version
  (general/graphlib/openjpeg2.xml); it is also the latest upstream
  release.
- Follow the documented cmake flags (Release build, shared library only)
  and install the man pages the base build copies into /usr/share/man.
- Install the libraries, CMake package files and pkg-config files into
  /usr/lib64; CMake's default for a /usr prefix on this image is lib.
- First Browneye build; replaces the unbuilt 2.3.1 spec.
