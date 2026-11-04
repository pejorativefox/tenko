Name:       c-ares
Version:    1.34.9
Release:    1
Summary:    C library for asynchronous DNS requests
License:    MIT
URL:        https://c-ares.org/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
c-ares is a C library for asynchronous DNS requests, including name
resolves.  It is used by Node.js for its DNS implementation.

%prep
%setup -q -n %{name}-%{version}

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_INSTALL_LIBDIR=lib64 ..
make
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} make install
popd

%files -f %{_sourcedir}/c-ares.filelist

%changelog
* Mon Nov  2 2026 browneye <build@browneye.invalid> 1.34.9-1
- Update to 1.34.9 (current LFS/BLFS r13.1 trunk version).

* Sun Nov 01 2026 Browneye Node.js wave <daspork@browneye.invalid> 1.34.8-1
- New package (BLFS r13.1 packages.ent c-ares-version 1.34.8).
- Source: https://github.com/c-ares/c-ares/releases/download/v1.34.8/c-ares-1.34.8.tar.gz
  md5 a0568780ffe1476160a6bbb4b6737261
  sha256 c222b6d681096f9444d2c4863d2c1174019e27cacca0a4a5c114d36dd7d7bf78
- Configure: cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib64
  (BLFS r13.1 command plus the distro's /usr/lib64 layout; the cmake
  4.4.3 RPM patches GNUInstallDirs to default to lib).
- Static filelist generated from the install tree.
