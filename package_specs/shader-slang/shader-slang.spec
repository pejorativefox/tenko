%global glslang_commit        d1f52c8993a501bd52d4fbd044bfeb9ecdceb9f4
%global spirv_tools_commit    b8c3b64b63758042576f6853d7f0abe9251460fa
%global spirv_headers_commit  86f980c731e62ae4eaf383d320449d71687936bf
%global miniz_commit          6ef6c68f4fcbb8287aa8edf9c6670804932f41c6
%global unordered_dense_commit 73f3cbb237e84d483afafc743f1f14ec53e12314
%global cmark_commit          924936d0427cb25a61169739a7660230bffa6ea6
%global fast_float_commit     e0b53eaf63c6d00e0725788ef1dbb759aa321d79

Name:       shader-slang
Version:    2026.22
Release:    1
Summary:    Slang shading language compiler
License:    Apache-2.0 WITH LLVM-exception AND Apache-2.0 AND MIT AND BSD-2-Clause AND BSD-3-Clause AND (Apache-2.0 OR MIT OR BSL-1.0)
URL:        https://github.com/shader-slang/slang
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
# Git submodules pinned by the v2026.22 tag, unpacked into external/.
Source1:    glslang-%{glslang_commit}.tar.gz
Source2:    spirv-tools-%{spirv_tools_commit}.tar.gz
Source3:    spirv-headers-%{spirv_headers_commit}.tar.gz
Source4:    miniz-%{miniz_commit}.tar.gz
Source5:    unordered_dense-%{unordered_dense_commit}.tar.gz
Source6:    cmark-%{cmark_commit}.tar.gz
Source7:    fast_float-%{fast_float_commit}.tar.gz
# Install libraries, standard modules and the pkg-config file under
# CMAKE_INSTALL_LIBDIR (upstream hard-codes lib/) and the headers under
# CMAKE_INSTALL_INCLUDEDIR, so they can go to /usr/include/slang (S-Lang
# owns /usr/include/slang.h).
Patch0:     %{name}-%{version}-install-dirs.patch

BuildRequires: cmake
BuildRequires: ninja
BuildRequires: gcc
BuildRequires: python
BuildRequires: pkgconf
BuildRequires: lz4
BuildRequires: lua
BuildRequires: vulkan-headers

%description
Slang is a shading language and compiler that targets SPIR-V, GLSL, HLSL,
Metal, WGSL, CUDA and C++.  This package installs the slangc command line
compiler and the slang dispatcher command, the libslang-compiler, libslang-glslang, libslang-glsl-module and
libslang-rt shared libraries with the precompiled standard modules, the
C/C++ API headers under /usr/include/slang, and the CMake and pkg-config
files.  The upstream Markdown documentation is not installed; it is at
https://shader-slang.org/docs/.

It is built without the LLVM backend (no prebuilt slang-llvm download),
without DXIL/DXC, the GFX/RHI runtime layers, the language server, the
interpreter, the replayer, tests and examples.  glslang, SPIRV-Tools and
SPIRV-Headers are the revisions pinned by upstream and are linked
statically into libslang-glslang; lz4, Lua (for the build-time slang-fiddle
generator) and the Vulkan headers come from the system.

%prep
%setup -q -n slang-%{version}
%patch -P 0 -p1
tar -xf %{SOURCE1} -C external/glslang --strip-components=1
tar -xf %{SOURCE2} -C external/spirv-tools --strip-components=1
tar -xf %{SOURCE3} -C external/spirv-headers --strip-components=1
tar -xf %{SOURCE4} -C external/miniz --strip-components=1
tar -xf %{SOURCE5} -C external/unordered_dense --strip-components=1
tar -xf %{SOURCE6} -C external/cmark --strip-components=1
tar -xf %{SOURCE7} -C external/fast_float --strip-components=1

%build
cmake -S . -B build -G Ninja                        \
      -DCMAKE_INSTALL_PREFIX=/usr                   \
      -DCMAKE_BUILD_TYPE=Release                    \
      -DCMAKE_INSTALL_LIBDIR=lib64                  \
      -DCMAKE_INSTALL_INCLUDEDIR=include/slang      \
      -DSLANG_VERSION_NUMERIC=%{version}            \
      -DSLANG_VERSION_FULL=%{version}               \
      -DSLANG_SLANG_LLVM_FLAVOR=DISABLE             \
      -DSLANG_ENABLE_DXIL=OFF                       \
      -DSLANG_EXCLUDE_DAWN=ON                       \
      -DSLANG_EXCLUDE_TINT=ON                       \
      -DSLANG_ENABLE_GFX=OFF                        \
      -DSLANG_ENABLE_SLANG_RHI=OFF                  \
      -DSLANG_ENABLE_TESTS=OFF                      \
      -DSLANG_ENABLE_EXAMPLES=OFF                   \
      -DSLANG_ENABLE_SLANGD=OFF                     \
      -DSLANG_ENABLE_SLANGI=OFF                     \
      -DSLANG_ENABLE_REPLAYER=OFF                   \
      -DSLANG_ENABLE_SLANG_PROXY=OFF                \
      -DSLANG_ENABLE_CUDA=OFF                       \
      -DSLANG_ENABLE_OPTIX=OFF                      \
      -DSLANG_ENABLE_NVAPI=OFF                      \
      -DSLANG_ENABLE_AFTERMATH=OFF                  \
      -DSLANG_ENABLE_XLIB=OFF                       \
      -DSLANG_ENABLE_RELEASE_DEBUG_INFO=OFF         \
      -DSLANG_ENABLE_SPLIT_DEBUG_INFO=OFF           \
      -DSLANG_STANDARD_MODULE_DEVELOP_BUILD=OFF     \
      -DSLANG_INSTALL_USER_SKILLS=OFF               \
      -DSLANG_USE_SYSTEM_LZ4=ON                     \
      -DSLANG_USE_SYSTEM_LUA=ON                     \
      -DSLANG_USE_SYSTEM_VULKAN_HEADERS=ON
ninja -C build %{?_smp_mflags}

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install
rm -rf %{buildroot}%{_docdir}/slang
lic=%{buildroot}%{_datadir}/licenses/%{name}
install -Dpm0644 LICENSE                          $lic/LICENSE
install -Dpm0644 external/glslang/LICENSE.txt     $lic/glslang-LICENSE.txt
install -Dpm0644 external/spirv-tools/LICENSE     $lic/spirv-tools-LICENSE
install -Dpm0644 external/spirv-headers/LICENSE   $lic/spirv-headers-LICENSE
install -Dpm0644 external/miniz/LICENSE           $lic/miniz-LICENSE
install -Dpm0644 external/unordered_dense/LICENSE $lic/unordered_dense-LICENSE
install -Dpm0644 external/cmark/COPYING           $lic/cmark-COPYING
install -Dpm0644 external/fast_float/LICENSE-MIT  $lic/fast_float-LICENSE-MIT

%check
export LD_LIBRARY_PATH=%{buildroot}%{_libdir}
slangc=%{buildroot}%{_bindir}/slangc
$slangc -version 2>&1 | tee version.txt
grep -qx '%{version}' version.txt
cat > check.slang << "EOF"
[shader("fragment")]
float4 fragmentMain(float4 color : COLOR0) : SV_Target
{
    return color * 0.5;
}
EOF
$slangc check.slang -entry fragmentMain -stage fragment -target spirv -o check.spv
od -An -N4 -tx1 check.spv | grep -q '03 02 23 07'
$slangc check.slang -entry fragmentMain -stage fragment -target glsl -profile glsl_150 -o check.glsl
grep -q '^#version' check.glsl
grep -q 'void main()' check.glsl

%files -f %{_sourcedir}/%{name}.filelist

%changelog
* Sat Nov 14 2026 tenko <build@tenko.invalid> 2026.22-1
- New package, not in the base set: latest upstream stable release
  (2026.22, checked 2026-11-14).  Needed by kitty to generate its shaders
  at build time and to compile custom shaders at runtime.  Built from the
  tag archive plus the pinned glslang, SPIRV-Tools, SPIRV-Headers, miniz,
  unordered_dense, cmark and fast_float submodule archives; no LLVM, DXIL,
  GFX/RHI, slangd or slangi.
