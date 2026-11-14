Name:       abseil-cpp
Version:    20260817.0
Release:    1
Summary:    C++ common libraries from Google (Abseil)
License:    Apache-2.0
URL:        https://abseil.io/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: gcc
BuildRequires: cmake
BuildRequires: ninja

%description
Abseil is an open-source collection of C++ library code designed to
augment the C++ standard library: strings, containers, hashing,
synchronization, time, status and logging utilities.  This package ships
the shared libraries, headers, pkg-config files and CMake package
configuration.  protobuf builds against it.

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
      -D BUILD_TESTING=OFF \
      -D ABSL_BUILD_TESTING=OFF \
      -D ABSL_PROPAGATE_CXX_STD=ON \
      -G Ninja ..
ninja %{?_smp_mflags}
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
install -Dm644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE

%files -f %{_sourcedir}/abseil-cpp.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 20260817.0-1
- New package, not in the base set: latest upstream stable release
  (20260817.0, checked 2026-11-14).  Needed by protobuf (protoc for
  netavark, podman stack, issue #67).
- Shared libraries built with C++17 propagated to consumers.
