Name:       intel-media-driver
Version:    26.3.5
Release:    1
Summary:    VA-API driver for Intel Gen8 and newer integrated GPUs
License:    MIT
URL:        https://github.com/intel/media-driver
Source0:    intel-media-%{version}.tar.gz
Prefix:     /usr

BuildRequires: cmake
BuildRequires: gcc
BuildRequires: intel-gmmlib
BuildRequires: libdrm
BuildRequires: libva
BuildRequires: ninja
BuildRequires: pkgconf

%description
The Intel media driver for VA-API implements hardware-accelerated video
decode, encode and processing on Intel integrated GPUs from Broadwell
onwards, as the iHD driver that libva loads from the DRI driver
directory.  It builds against libva and intel-gmmlib.  The legacy
cmrtlib runtime is not built.

%prep
%setup -q -n media-driver-intel-media-%{version}

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D CMAKE_BUILD_TYPE=Release \
      -D LIBVA_DRIVERS_PATH=/usr/lib64/dri \
      -D BUILD_CMRTLIB=OFF \
      -D MEDIA_BUILD_FATAL_WARNINGS=OFF \
      -D MEDIA_RUN_TEST_SUITE=OFF \
      -G Ninja ..
ninja %{?_smp_mflags}
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/intel-media-driver.filelist

%changelog
* Fri Nov 20 2026 tenko <build@tenko.invalid> 26.3.5-1
- New package, not in the base set: latest upstream stable release
  (intel-media-26.3.5, the 2026Q3 quarterly, checked 2026-11-20), built
  against libva 2.24.1 and intel-gmmlib 22.10.2.
- The driver installs as iHD_drv_video.so in /usr/lib64/dri, next to
  the Mesa VA drivers.  The legacy cmrtlib runtime is not built
  (BUILD_CMRTLIB=OFF).
- Warnings are not fatal: GCC 16 reports a false-positive
  -Warray-bounds inside libstdc++ headers from a static std::map
  initializer (media_ddi_encode_hevc.cpp).
