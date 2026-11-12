Name:       tenko-base-build
Version:    6
Release:    5
Epoch:      1
Summary:    Tenko Linux development environment (runtime base + toolchain)
License:    MIT
URL:        https://github.com/pejorativefox/tenko
Prefix:     /usr

# tenko-base-runtime plus the toolchain baseline (tenko-buildroot) plus the
# development extras a build host or interactive developer expects.
# Package builds do not rely on this meta: they start from tenko-buildroot
# and add their spec's BuildRequires (issue #58).
Requires:   tenko-base-runtime
Requires:   tenko-buildroot
Requires:   gperf
Requires:   texinfo
Requires:   tcl
Requires:   expect
Requires:   dejagnu
Requires:   glibc-i18n
Requires:   python-setuptools
Requires:   python-wheel
Requires:   python-flit-core
Requires:   python-packaging
Requires:   python-markupsafe
Requires:   python-jinja
Requires:   groff
Requires:   man-db
Requires:   man-pages

%description
The Tenko development environment: tenko-base-runtime plus the toolchain
baseline from tenko-buildroot (GCC, binutils, autotools, gettext,
meson/ninja/cmake, kernel headers, rpm and the Tenko macros) and common
development extras: the GCC LTO plugin, gperf, texinfo, tcl/expect/dejagnu
for test suites, glibc locale sources for localedef, the Python build
backends and the manual pages.  Development headers and .pc files ship in
the runtime packages themselves.

Package-specific build inputs (for example Mesa's LLVM/Clang/SPIR-V chain)
are BuildRequires of the specs that need them, not part of this profile.

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/tenko
touch %{buildroot}/usr/share/tenko/base-build

%files -f %{_sourcedir}/tenko-base-build.filelist

%changelog
* Thu Nov 12 2026 tenko <build@tenko.invalid> 6-5
- Stop requiring gcc-lto: gcc carries the LTO backend and linker plugin
  again, so gcc alone links Rust and -flto (issue #63).

* Wed Nov 11 2026 tenko <build@tenko.invalid> 6-4
- Layer on tenko-buildroot instead of listing the toolchain directly.
- Drop the Mesa CLC chain (llvm, llvm-devel, llvm-static, clang-libs,
  clang-devel, clang-resource-filesystem, spirv-headers, spirv-tools,
  spirv-llvm-translator, python-mako, python-pyyaml) and vulkan-headers:
  mesa.spec and vulkan-loader.spec declare them as BuildRequires, so a
  build installs them when needed (issue #58).

* Mon Nov 09 2026 tenko <build@tenko.invalid> 6-3
- Carry vulkan-headers: the Vulkan loader builds from the Khronos
  headers, and Mesa installs Vulkan ICDs that the loader loads.
- Carry clang-devel: Mesa's Intel CLC includes clang/Config/config.h
  and the Clang C++ headers, which the runtime clang packages do not
  ship.  A fresh build image needs them explicitly.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-2
- Carry the Mesa Intel CLC build chain: llvm-devel, llvm, llvm-static,
  clang-libs, clang-resource-filesystem, spirv-headers, spirv-tools,
  spirv-llvm-translator, python-mako and python-pyyaml (issue #51).
  Adding iris/crocus makes mesa build mesa_clc, which needs
  LLVMSPIRVLib.pc, SPIRV-Tools.pc, libclang-cpp, opencl-c.h and the
  Python Mako/PyYAML modules.  None of these are Mesa runtime
  dependencies.
- Require llvm and llvm-static explicitly: LLVMExports.cmake checks
  every tool binary and static archive when a consumer calls
  find_package(LLVM), and the published llvm-devel does not pull them
  in.  This replaces the zero-length archives and stub tools used in
  the local test image.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-1
- Rebase on the Tenko 6 distro release with Epoch 1 so installs carrying
  the old 13.1 EVR upgrade cleanly.
- Drop the browneye-base-build Obsoletes/Provides alias and the old marker
  cleanup; no Browneye installs remain.

* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-3
- Rename browneye-base-build to tenko-base-build and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 13.1-2
- Drop the gcc-devel, binutils-devel, glibc-devel, openssl-devel and
  perl-devel requirements: the -devel subpackages are gone and their
  payload now ships in the runtime packages (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-1
- New build profile: browneye-base-runtime + GCC/binutils toolchain,
  autotools, gettext/texinfo, meson/ninja/cmake, devel and static
  subpackages, Python build backends (size audit B3/B4)
