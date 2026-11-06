Name:       drpm
Version:    0.5.3
Release:    1
Summary:    A library for making, reading and applying deltarpm packages
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: cmake
BuildRequires: rpm
BuildRequires: zlib
BuildRequires: bzip2
BuildRequires: xz
BuildRequires: zstd
BuildRequires: openssl

%description
drpm is a library for making, reading and applying deltarpm packages.  A
deltarpm stores the difference between two versions of an RPM package, so a
client only downloads the changed parts instead of the whole package.

%prep
%setup -q

%build
mkdir build
pushd build
cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr \
      -DCMAKE_INSTALL_LIBDIR=lib64 \
      -DENABLE_TESTS=0 ..
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
%make_install
popd

%files -f %{_sourcedir}/drpm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.5.3-1
- Update 0.4.1 -> 0.5.3: not in the base set; latest upstream stable
  2026-11-05
  (https://github.com/rpm-software-management/drpm/releases).
- Source is the GitHub release archive, which extracts to drpm-0.5.3.
- Build with the upstream CMake options: -DENABLE_TESTS=0 (the test
  suite needs cmocka) and the default WITH_ZSTD=1.  zlib, bzip2, xz,
  zstd and libcrypto are all present in the base image.
- Set CMAKE_INSTALL_LIBDIR=lib64 because the distro CMake defaults
  GNUInstallDirs to lib.
