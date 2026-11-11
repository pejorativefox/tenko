Name:       glslang
Version:    16.6.0
Release:    1
Summary:    Khronos reference compiler and validator for GLSL and HLSL
License:    Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND MIT AND AML-glslang
URL:        https://github.com/KhronosGroup/glslang
Prefix:     /usr
Source0:    glslang-16.6.0.tar.gz

BuildRequires: cmake
BuildRequires: ninja
BuildRequires: python
BuildRequires: gcc

%description
glslang is the Khronos reference front end for OpenGL GLSL/ESSL and HLSL
shaders and the reference SPIR-V generator.  It installs the glslang
compiler and its backwards-compatible glslangValidator command, together
with the libglslang and libSPIRV shared libraries, the development headers
and the CMake package files needed by programs that compile shaders
in-process.

The SPIR-V optimizer integration (ENABLE_OPT) is disabled: it requires the
exact SPIRV-Tools revision pinned by upstream and is not needed to parse or
validate GLSL.  HLSL input is enabled, but without the optimizer it can
produce unoptimized SPIR-V.

Version 16.6.0 is the latest stable upstream release (tag 16.6.0,
2026-09-10).

%prep
%setup -q

%build
cmake -S . -B build -G Ninja          \
      -DCMAKE_INSTALL_PREFIX=/usr     \
      -DCMAKE_BUILD_TYPE=Release      \
      -DCMAKE_INSTALL_LIBDIR=lib64    \
      -DBUILD_SHARED_LIBS=ON          \
      -DBUILD_EXTERNAL=OFF            \
      -DENABLE_OPT=OFF                \
      -DGLSLANG_TESTS=OFF             \
      -DGLSLANG_ENABLE_INSTALL=ON
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install

%files -f %{_sourcedir}/glslang.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 16.6.0-1
- Initial package: glslang 16.6.0, the latest stable upstream release
  (tag 16.6.0, 2026-09-10).  Ships glslangValidator/glslang, the shared
  libglslang/libSPIRV libraries and headers; the optimizer is disabled
  because it requires the exact SPIRV-Tools revision pinned upstream.
