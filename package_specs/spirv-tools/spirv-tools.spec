Name:       spirv-tools
Version:    2026.4
Release:    1
Summary:    API and command-line tools for processing SPIR-V modules
License:    Apache-2.0
Prefix:     /usr
Source0:    SPIRV-Tools-v2026.4.tar.gz

# The headers are installed by spirv-headers; upstream wants a source tree,
# but passing the installed prefix (/usr) is enough for the include check.
BuildRequires: spirv-headers

%description
SPIRV-Tools provides the SPIR-V assembler, binary parser, disassembler,
validator, optimizer, linker and reducer, plus the libSPIRV-Tools libraries
and development files.  Mesa uses the libraries and pkg-config metadata when
it builds its Intel OpenCL C compiler (mesa_clc).

The package keeps upstream's static libraries: SPIRV-Tools.pc links them, so
the Mesa RPM has no runtime dependency on SPIRV-Tools (the mesa_clc helper is
a build-time tool and is not installed).  The shared library is installed as
well for consumers that link it explicitly.

Version 2026.4 matches the upstream release tag v2026.4; the generated
SPIRV-Tools.pc reports 2026.4.1, which is how upstream numbers the
post-release pkg-config version.

%prep
%setup -q -n SPIRV-Tools-2026.4

%build
cmake -S . -B build -G Ninja          \
      -DCMAKE_INSTALL_PREFIX=/usr     \
      -DCMAKE_BUILD_TYPE=Release      \
      -DCMAKE_INSTALL_LIBDIR=lib64    \
      -DSPIRV-Headers_SOURCE_DIR=%{_prefix} \
      -DSPIRV_SKIP_TESTS=ON           \
      -DSPIRV_TOOLS_BUILD_STATIC=ON   \
      -DSPIRV_WERROR=OFF
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install

%files -f %{_sourcedir}/spirv-tools.filelist

%changelog
* Sun Nov 08 2026 browneye <build@browneye.invalid> 2026.4-1
- Initial package: SPIRV-Tools 2026.4, the latest stable upstream release
  (tag v2026.4 / vulkan-sdk-1.4.363.0).  Ship the assembler/optimizer tools
  and the static libraries that SPIRV-Tools.pc links, so Mesa can build
  mesa_clc without adding a SPIRV-Tools runtime dependency to the Mesa RPM
  (issue #51).
