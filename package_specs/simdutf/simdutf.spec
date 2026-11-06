Name:       simdutf
Version:    9.3.3
Release:    1
Summary:    Unicode validation and transcoding at billions of characters per second
License:    MIT
URL:        https://github.com/simdutf/simdutf
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
simdutf is a C++ library for fast Unicode validation and transcoding using
SIMD instructions.  Node.js can link against the shared system copy with
--shared-simdutf instead of its bundled deps/v8/third_party copy.

%prep
%setup -q -n %{name}-%{version}

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D CMAKE_BUILD_TYPE=Release  \
      -D BUILD_SHARED_LIBS=ON      \
      -D SIMDUTF_CXX_STANDARD=20   \
      -G Ninja ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/simdutf.filelist

%changelog
* Mon Nov  2 2026 browneye <build@browneye.invalid> 9.3.3-1
- Update to 9.3.3 (current upstream version).

* Sun Nov 01 2026 Browneye Node.js wave <daspork@browneye.invalid> 9.2.1-1
- New package (tenko.lock simdutf-version 9.2.1).
- Source: https://github.com/simdutf/simdutf/archive/v9.2.1/simdutf-9.2.1.tar.gz
  md5 1d1c7231821b06e459e83c1a08f8a6fc
  sha256 582f9d0dcf578f6d4766fa29ea12a7f2f02bd3c6ad9e0cf35a8e0ec8478eba4b
- Configure: cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib64
  -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON -DSIMDUTF_CXX_STANDARD=20
  -G Ninja (plus the distro's /usr/lib64 layout).
- Static filelist generated from the install tree.
