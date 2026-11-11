Name:       spirv-llvm-translator
Version:    23.1.3
Release:    1
Summary:    LLVM IR to SPIR-V translator
License:    NCSA
URL:        https://github.com/KhronosGroup/SPIRV-LLVM-Translator
Prefix:     /usr
Source0:    SPIRV-LLVM-Translator-v23.1.3.tar.gz

# The translator's CMake package check walks every file referenced by the
# installed LLVM CMake exports, so the static archives and tools packages must
# be present too.  Fedora carries the same requirements on llvm-devel.
BuildRequires: llvm-devel, llvm-static, llvm, spirv-headers

%description
The Khronos LLVM/SPIR-V bi-directional translator: libLLVMSPIRVLib, its
pkg-config metadata and the standalone llvm-spirv tool.  Mesa uses
LLVMSPIRVLib at build time for its Intel OpenCL C compiler (mesa_clc).

Version 23.1.3 is the latest stable upstream tag; it is built against the
distribution LLVM 23.1, matching the translator's BASE_LLVM_VERSION.

%prep
%setup -q -n SPIRV-LLVM-Translator-23.1.3

%build
cmake -S . -B build -G Ninja                     \
      -DCMAKE_INSTALL_PREFIX=/usr                \
      -DCMAKE_BUILD_TYPE=Release                 \
      -DBUILD_SHARED_LIBS=ON                     \
      -DLLVM_LIBDIR_SUFFIX=64                    \
      -DLLVM_EXTERNAL_SPIRV_HEADERS_SOURCE_DIR=%{_prefix} \
      -DLLVM_SPIRV_INCLUDE_TESTS=OFF
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install

%files -f %{_sourcedir}/spirv-llvm-translator.filelist

%changelog
* Sun Nov 08 2026 browneye <build@browneye.invalid> 23.1.3-1
- Initial package: SPIRV-LLVM-Translator 23.1.3, the latest stable upstream
  tag, built against the distribution LLVM 23.1.  Mesa needs LLVMSPIRVLib.pc
  and libLLVMSPIRVLib when it builds mesa_clc (issue #51).
- Build against the real llvm-static and llvm packages instead of the
  zero-length archive and stub-tool workaround that was used in the local
  test image; the LLVM CMake exports reference those files directly.
