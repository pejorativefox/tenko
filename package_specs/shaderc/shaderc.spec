%global glslang_commit        e1b562a8bed273a02f30b59b66a5d499793cede5
%global spirv_tools_commit    ef96ed763b43b59b33b31b362f09a02b729fa1c9
%global spirv_headers_commit  04fd3caa1e8267e4d95c806cad901181728e1006

Name:       shaderc
Version:    2026.4
Release:    1
Summary:    Collection of tools and libraries for Vulkan shader compilation (glslc)
License:    Apache-2.0 AND MIT
URL:        https://github.com/google/shaderc
Prefix:     /usr
Source0:    shaderc-v%{version}.tar.gz
# Git submodules pinned by the v2026.4 DEPS file, unpacked into third_party/.
Source1:    glslang-%{glslang_commit}.tar.gz
Source2:    spirv-tools-%{spirv_tools_commit}.tar.gz
Source3:    spirv-headers-%{spirv_headers_commit}.tar.gz
# glslang and SPIRV-Tools are vendored and statically linked into glslc and
# libshaderc, so their install rules must stay off: the system glslang and
# spirv-tools packages own those files, and upstream's generator-expression
# on the skip flag otherwise makes the glslang install export fail.
Patch0:     %{name}-%{version}-no-vendor-install.patch

BuildRequires: cmake
BuildRequires: ninja
BuildRequires: gcc
BuildRequires: python

%description
shaderc is a collection of tools and libraries for Vulkan shader
compilation: the glslc command line compiler, GLSL-to-SPIR-V with a
clang-style interface, and the libshaderc_shared library for compiling
shaders in-process.

glslc is built from the upstream release archive together with the
glslang, SPIRV-Tools and SPIRV-Headers revisions pinned by the v2026.4
DEPS file, linked statically into the glslc binary and libshaderc; their
install rules are disabled so the system glslang and spirv-tools packages
keep owning those files.  Tests, examples, the copyright check and the
WGSL (Tint) output are not built.

%prep
%setup -q -n shaderc-%{version}
%patch -P 0 -p1
# GitHub source archives do not include submodule directories.
mkdir -p third_party/glslang third_party/spirv-tools third_party/spirv-headers
tar -xf %{SOURCE1} -C third_party/glslang --strip-components=1
tar -xf %{SOURCE2} -C third_party/spirv-tools --strip-components=1
tar -xf %{SOURCE3} -C third_party/spirv-headers --strip-components=1

%build
cmake -S . -B build -G Ninja                          \
      -DCMAKE_INSTALL_PREFIX=/usr                     \
      -DCMAKE_BUILD_TYPE=Release                      \
      -DCMAKE_INSTALL_LIBDIR=lib64                    \
      -DSHADERC_SKIP_TESTS=ON                         \
      -DSHADERC_SKIP_EXAMPLES=ON                      \
      -DSHADERC_SKIP_COPYRIGHT_CHECK=ON               \
      -DSHADERC_ENABLE_WGSL_OUTPUT=OFF
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install
lic=%{buildroot}%{_datadir}/licenses/%{name}
install -Dpm0644 LICENSE                            $lic/LICENSE
install -Dpm0644 third_party/glslang/LICENSE.txt    $lic/glslang-LICENSE.txt
install -Dpm0644 third_party/spirv-tools/LICENSE    $lic/spirv-tools-LICENSE
install -Dpm0644 third_party/spirv-headers/LICENSE  $lic/spirv-headers-LICENSE

%check
glslc=%{buildroot}%{_bindir}/glslc
$glslc --version 2>&1 | tee version.txt
grep -q 'shaderc' version.txt
cat > check.comp << "EOF"
#version 450
layout(local_size_x = 1) in;
void main() {}
EOF
$glslc -o check.spv check.comp
od -An -N4 -tx1 check.spv | grep -q '03 02 23 07'

%files -f %{_sourcedir}/%{name}.filelist

%changelog
* Wed Nov 18 2026 tenko <build@tenko.invalid> 2026.4-1
- New package, not in the base set: latest upstream stable release
  (2026.4, checked 2026-11-18).  Provides glslc, the SPIR-V compiler
  required by ggml's Vulkan backend in llama-cpp.  Built from the tag
  archive plus the glslang, SPIRV-Tools and SPIRV-Headers revisions
  pinned by the v2026.4 DEPS file, statically linked; their install rules
  are disabled so the system glslang and spirv-tools keep owning those
  files.
