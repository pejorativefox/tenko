Name:       spirv-headers
Version:    1.5.5
Release:    1
Summary:    Khronos SPIR-V headers and registry files
License:    MIT
URL:        https://github.com/KhronosGroup/SPIRV-Headers
Prefix:     /usr
Source0:    SPIRV-Headers-cb42dec3830d3ac67fa449ecdc0c0f73d5e74498.tar.gz

%description
The Khronos SPIR-V headers: the C and C++ declarations, the JSON grammar
for the core instruction set and the extended instruction sets, and the
XML registry.  SPIRV-Tools and SPIRV-LLVM-Translator build against these
headers.

The package version follows the upstream CMake project version (1.5.5).
Source0 is the SPIRV-Headers commit pinned by SPIRV-LLVM-Translator 23.1.3
(cb42dec, 2026-09-24); the newest Vulkan SDK tag (vulkan-sdk-1.4.363.0)
predates the SPV_INTEL_subgroup_bitcast_shuffle definitions that translator
release needs.  SPIRV-Tools 2026.4 builds against the same headers.

%prep
%setup -q -n SPIRV-Headers-cb42dec3830d3ac67fa449ecdc0c0f73d5e74498

%build
cmake -S . -B build -G Ninja      \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_BUILD_TYPE=Release  \
      -DSPIRV_HEADERS_ENABLE_TESTS=OFF
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install

%files -f %{_sourcedir}/spirv-headers.filelist

%changelog
* Sun Nov 08 2026 browneye <build@browneye.invalid> 1.5.5-1
- Initial package: SPIRV-Headers at upstream CMake project version 1.5.5.
  Source0 is commit cb42dec, the revision pinned by SPIRV-LLVM-Translator
  23.1.3; the latest Vulkan SDK tag (vulkan-sdk-1.4.363.0) is too old for
  that translator release.  Build dependency of SPIRV-Tools and
  SPIRV-LLVM-Translator for Mesa's Intel CLC (issue #51).
