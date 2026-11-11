Name:       llvm
Version:    23.1.0
Release:    3
Summary:    The LLVM Project is a collection of modular and reusable compiler and toolchain technologies. 
License:    UIUC
URL:        https://llvm.org/
Source0:    llvm-project-%{version}.src.tar.xz
Prefix:     /usr

Requires:   llvm-libs = %{version}-%{release}

%description
The LLVM Project is a collection of modular and reusable compiler and
toolchain technologies.  This package contains the LLVM command-line tools
and binaries; the runtime libraries, development data, static archives and
the Clang toolchain are in separate subpackages (matching the granularity of
Fedora's llvm source package).

%prep
%setup -q -n llvm-project-%{version}.src
grep -rl '#!.*python$' . | xargs -r sed -i '1s/python$/python3/'
sed -i 's/utility/tool/' llvm/utils/FileCheck/CMakeLists.txt

%build
mkdir -p llvm/build
pushd llvm/build
CC=gcc CXX=g++ cmake -D CMAKE_INSTALL_PREFIX=/usr           \
      -D CMAKE_SKIP_INSTALL_RPATH=ON                        \
      -D LLVM_ENABLE_FFI=ON                                 \
      -D CMAKE_BUILD_TYPE=Release                           \
      -D LLVM_BUILD_LLVM_DYLIB=ON                           \
      -D LLVM_LINK_LLVM_DYLIB=ON                            \
      -D LLVM_ENABLE_RTTI=ON                                \
      -D LLVM_LIBDIR_SUFFIX=64                              \
      -D LLVM_TARGETS_TO_BUILD="host;AMDGPU"                \
      -D LLVM_ENABLE_PROJECTS=clang                         \
      -D LLVM_ENABLE_RUNTIMES=compiler-rt                   \
      -D LLVM_BINUTILS_INCDIR=/usr/include                  \
      -D LLVM_INCLUDE_BENCHMARKS=OFF                        \
      -D CLANG_DEFAULT_PIE_ON_LINUX=ON                      \
      -D CLANG_CONFIG_FILE_SYSTEM_DIR=/etc/clang            \
      -W no-author -G Ninja ..
ninja %{?_smp_mflags}
popd

%install
rm -rf %{buildroot}
pushd llvm/build
DESTDIR=%{buildroot} ninja install
popd
mkdir -p %{buildroot}/etc/clang
for i in clang clang++; do
    echo -fstack-protector-strong > %{buildroot}/etc/clang/$i.cfg
done

%package libs
Summary:    LLVM runtime shared libraries
License:    UIUC
Provides:   libLLVM.so.23.1
Provides:   libLTO.so.23.1
Provides:   libRemarks.so.23.1

%description libs
The LLVM runtime shared libraries: libLLVM, libLTO, libRemarks and the
LLVMgold linker plugin.  This is all Mesa's llvmpipe driver needs; it does
not pull in the compiler, Clang, static archives or development data.

%package devel
Summary:    LLVM development headers, CMake files and linker symlinks
License:    UIUC
Requires:   llvm-libs = %{version}-%{release}

%description devel
Development data for LLVM: the headers (including llvm-c), CMake package
files, the unversioned shared-library symlinks and llvm-config.  Static
archives are in llvm-static.

%package static
Summary:    LLVM and Clang static libraries
License:    UIUC

%description static
All LLVM, Clang and compiler-rt static archives (.a).  Kept separate so a
runtime or development install does not carry half a gigabyte of archives.

%package -n clang
Summary:    C language family frontend for LLVM
License:    UIUC
Requires:   clang-libs = %{version}-%{release}
Requires:   clang-resource-filesystem = %{version}-%{release}

%description -n clang
The Clang compiler driver and the clang/clang++/clang-cpp/clang-cl entry
points.  The shared libraries and builtin headers are separate packages.

%package -n clang-libs
Summary:    Clang runtime shared libraries
License:    UIUC
Requires:   llvm-libs = %{version}-%{release}
Provides:   libclang-cpp.so.23.1
Provides:   libclang.so.23.1

%description -n clang-libs
The Clang runtime shared libraries (libclang-cpp and the libclang C API).

%package -n clang-devel
Summary:    Clang development headers, CMake files and linker symlinks
License:    UIUC
Requires:   clang-libs = %{version}-%{release}
Requires:   llvm-devel = %{version}-%{release}

%description -n clang-devel
Development data for Clang: the headers (including clang-c), CMake package
files, unversioned shared-library symlinks and clang-tblgen.

%package -n clang-tools-extra
Summary:    Extra Clang tools
License:    UIUC
Requires:   clang = %{version}-%{release}
Requires:   clang-libs = %{version}-%{release}
Requires:   /usr/bin/python3

%description -n clang-tools-extra
Additional Clang-based tools: clang-format, clang-check, clang-refactor,
clang-repl, diagtool, c-index-test, the offload/arch helpers and their
support scripts.

%package -n clang-analyzer
Summary:    Clang static analyzer tools
License:    UIUC
Requires:   clang = %{version}-%{release}
Requires:   /usr/bin/python3

%description -n clang-analyzer
The Clang static analyzer front ends: scan-build, scan-build-py, scan-view,
analyze-build and intercept-build, plus the libear/libscanbuild Python
modules and the ScanView data files.

%package -n clang-resource-filesystem
Summary:    Clang builtin headers and resource files
License:    UIUC

%description -n clang-resource-filesystem
The versioned Clang resource directory: builtin and sanitizer headers,
ignore lists and hwasan_symbolize.  Clang needs this package to compile.

%package -n compiler-rt
Summary:    Compiler-rt runtime libraries
License:    UIUC
Requires:   clang-resource-filesystem = %{version}-%{release}

%description -n compiler-rt
The compiler-rt runtime libraries under /usr/lib/clang/23/lib: the
sanitizer/shared runtimes and the crtbegin/crtend objects.  The matching
static archives are in llvm-static.

%package all
Summary:    Everything from the LLVM source package
License:    UIUC
Requires:   llvm = %{version}-%{release}
Requires:   llvm-libs = %{version}-%{release}
Requires:   llvm-devel = %{version}-%{release}
Requires:   llvm-static = %{version}-%{release}
Requires:   clang = %{version}-%{release}
Requires:   clang-libs = %{version}-%{release}
Requires:   clang-devel = %{version}-%{release}
Requires:   clang-tools-extra = %{version}-%{release}
Requires:   clang-analyzer = %{version}-%{release}
Requires:   clang-resource-filesystem = %{version}-%{release}
Requires:   compiler-rt = %{version}-%{release}

%description all
Meta-package that installs every binary package produced from the LLVM
source package, preserving the old "install everything" behaviour.

%files -f %{_sourcedir}/llvm.filelist
%files libs -f %{_sourcedir}/llvm-libs.filelist
%files devel -f %{_sourcedir}/llvm-devel.filelist
%files static -f %{_sourcedir}/llvm-static.filelist
%files -n clang -f %{_sourcedir}/clang.filelist
%files -n clang-libs -f %{_sourcedir}/clang-libs.filelist
%files -n clang-devel -f %{_sourcedir}/clang-devel.filelist
%files -n clang-tools-extra -f %{_sourcedir}/clang-tools-extra.filelist
%files -n clang-analyzer -f %{_sourcedir}/clang-analyzer.filelist
%files -n clang-resource-filesystem -f %{_sourcedir}/clang-resource-filesystem.filelist
%files -n compiler-rt -f %{_sourcedir}/compiler-rt.filelist
%files all


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 23.1.0-3
- Install into /usr/lib64 like the rest of the distro: LLVM_LIBDIR_SUFFIX=64
  moves the runtime libraries, CMake packages, linker symlinks, static
  archives and the Clang resource directory out of /usr/lib.  This removes
  the need for xorg-server's -rpath-link workaround and the /usr/lib entry
  that image and dependency builds had to add to /etc/ld.so.conf.
- Pass %{?_smp_mflags} to ninja: a bare `ninja` ignored the rpm job limit and
  spawned cores+2 jobs, which is enough to OOM a 16 GB build host during
  clang Sema.
* Sun Nov 01 2026 browneye <build@browneye.invalid> 23.1.0-2
- Fedora-style split: llvm tools, llvm-libs, llvm-devel, llvm-static,
  clang, clang-libs, clang-devel, clang-tools-extra, clang-analyzer,
  clang-resource-filesystem, compiler-rt and the llvm-all meta.  Version
  and source are unchanged; static archives and headers are no longer part
  of the runtime or tools packages (size audit P0).

* Tue Jun 13 2023 Chris Statzer <chris.statzer@gmail.com> 16.0.5
- Initial RPM
