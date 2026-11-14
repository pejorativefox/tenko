Name:       protobuf
Version:    36.2
Release:    1
Summary:    Protocol Buffers: compiler and C++ runtime
License:    BSD-3-Clause AND MIT
URL:        https://protobuf.dev/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: gcc
BuildRequires: cmake
BuildRequires: ninja
BuildRequires: abseil-cpp
BuildRequires: zlib

%description
Protocol Buffers are Google's language-neutral, platform-neutral mechanism
for serializing structured data.  This package ships the protoc compiler,
the libprotobuf, libprotobuf-lite, libprotoc and upb libraries, their
headers, pkg-config and CMake files, and the well-known type definitions
under /usr/include/google/protobuf.  It builds against the system
abseil-cpp; utf8_range is the copy bundled in the release tarball
(MIT).

%prep
%setup -q

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D CMAKE_BUILD_TYPE=Release \
      -D CMAKE_CXX_STANDARD=17 \
      -D BUILD_SHARED_LIBS=ON \
      -D CMAKE_SKIP_INSTALL_RPATH=ON \
      -D protobuf_BUILD_SHARED_LIBS=ON \
      -D protobuf_BUILD_TESTS=OFF \
      -D protobuf_BUILD_CONFORMANCE=OFF \
      -D protobuf_BUILD_EXAMPLES=OFF \
      -D protobuf_ABSL_PROVIDER=package \
      -D protobuf_LOCAL_DEPENDENCIES_ONLY=ON \
      -D protobuf_WITH_ZLIB=ON \
      -G Ninja ..
ninja %{?_smp_mflags}
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
install -Dm644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE
install -Dm644 third_party/utf8_range/LICENSE \
    %{buildroot}%{_licensedir}/%{name}/LICENSE.utf8_range

%files -f %{_sourcedir}/protobuf.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 36.2-1
- New package, not in the base set: latest upstream stable release
  (36.2, checked 2026-11-14).  Provides protoc for netavark's
  tonic-prost-build step (podman stack, issue #67).
- Shared libraries, built against the system abseil-cpp; tests off.
