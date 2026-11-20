Name:       intel-gmmlib
Version:    22.10.2
Release:    1
Summary:    Intel Graphics Memory Management Library
License:    MIT
URL:        https://github.com/intel/gmmlib
Source0:    intel-gmmlib-%{version}.tar.gz
Prefix:     /usr

BuildRequires: cmake
BuildRequires: gcc
BuildRequires: ninja

%description
The Intel Graphics Memory Management Library provides device-specific
memory allocation, surface layout and cache-policy management for
Intel graphics user-mode drivers.  It ships the libigdgmm runtime
library together with the headers and pkg-config file that
intel-media-driver builds against.

%prep
%setup -q -n gmmlib-intel-gmmlib-%{version}

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D CMAKE_BUILD_TYPE=Release \
      -D RUN_TEST_SUITE=OFF \
      -G Ninja ..
ninja %{?_smp_mflags}
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/intel-gmmlib.filelist

%changelog
* Fri Nov 20 2026 tenko <build@tenko.invalid> 22.10.2-1
- New package, not in the base set: the gmmlib release that
  intel-media-driver 26.3.5 builds against (latest tag, checked
  2026-11-20).
- Unit tests are not built (RUN_TEST_SUITE=OFF).
