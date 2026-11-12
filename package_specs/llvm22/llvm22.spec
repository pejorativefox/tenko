Name:       llvm22
Version:    22.1.8
Release:    2
Summary:    LLVM and Clang 22 toolchain, installable alongside LLVM 23
License:    Apache-2.0 WITH LLVM-exception
URL:        https://llvm.org/
Source0:    llvm-project-%{version}.src.tar.xz
Prefix:     /usr

BuildRequires: cmake
BuildRequires: ninja
BuildRequires: gcc
BuildRequires: binutils
BuildRequires: make
BuildRequires: python
BuildRequires: zlib
BuildRequires: libffi
BuildRequires: ncurses
BuildRequires: pkgconf

%description
LLVM 22 with the matching Clang, compiler-rt runtimes and development data.
The whole toolchain is installed under /usr/lib64/llvm22 so it can coexist
with the distribution llvm 23 packages.  Every command is linked into
/usr/bin with a -22 suffix (clang-22, clang++-22, llvm-config-22, ...).
Build against it with llvm-config-22 or
-DLLVM_DIR=/usr/lib64/llvm22/lib/cmake/llvm.

%prep
%setup -q -n llvm-project-%{version}.src
grep -rl '#!.*python$' . | xargs -r sed -i '1s/python$/python3/'
sed -i 's/utility/tool/' llvm/utils/FileCheck/CMakeLists.txt

%build
mkdir -p llvm/build
pushd llvm/build
CC=gcc CXX=g++ cmake -G Ninja ..                             \
      -D CMAKE_INSTALL_PREFIX=%{_libdir}/llvm22              \
      -D CMAKE_BUILD_TYPE=Release                            \
      -D CMAKE_INSTALL_RPATH='$ORIGIN/../lib'                \
      -D CMAKE_BUILD_WITH_INSTALL_RPATH=ON                   \
      -D LLVM_ENABLE_FFI=ON                                  \
      -D LLVM_BUILD_LLVM_DYLIB=ON                            \
      -D LLVM_LINK_LLVM_DYLIB=ON                             \
      -D LLVM_ENABLE_RTTI=ON                                 \
      -D LLVM_TARGETS_TO_BUILD="host;AMDGPU;ARM;AArch64;X86;WebAssembly;RISCV" \
      -D LLVM_ENABLE_PROJECTS=clang                          \
      -D LLVM_ENABLE_RUNTIMES=compiler-rt                    \
      -D LLVM_BINUTILS_INCDIR=/usr/include                   \
      -D LLVM_INCLUDE_BENCHMARKS=OFF                         \
      -D LLVM_INSTALL_BINUTILS_SYMLINKS=OFF                   \
      -D CLANG_DEFAULT_PIE_ON_LINUX=ON                       \
      -D CLANG_CONFIG_FILE_SYSTEM_DIR=%{_sysconfdir}/clang-22 \
      -W no-author
ninja %{?_smp_mflags}
popd

%install
rm -rf %{buildroot}
pushd llvm/build
DESTDIR=%{buildroot} ninja install
popd
mkdir -p %{buildroot}%{_sysconfdir}/clang-22
for i in clang clang++; do
    echo -fstack-protector-strong > %{buildroot}%{_sysconfdir}/clang-22/$i.cfg
done
# Link every command into /usr/bin with a -22 suffix so the two LLVM
# majors do not collide on the command names.
mkdir -p %{buildroot}%{_bindir}
for binary in %{buildroot}%{_libdir}/llvm22/bin/*; do
    name=${binary##*/}
    case "$name" in
        *-22) link=$name ;;
        *)    link=$name-22 ;;
    esac
    ln -sf ../lib64/llvm22/bin/$name %{buildroot}%{_bindir}/$link
done

%files -f %{_sourcedir}/llvm22.filelist

%changelog
* Thu Nov 12 2026 tenko <build@tenko.invalid> 22.1.8-2
- Build the ARM, AArch64, X86, WebAssembly and RISC-V backends in addition
  to host and AMDGPU, so llvm-config-22 --libs accepts those target
  components (for example arm and webassembly).

* Thu Nov 12 2026 tenko <build@tenko.invalid> 22.1.8-1
- New package, not in the base set: LLVM 22.1.8, the latest stable upstream
  release on the 22 branch (checked 2026-11-12), installed in a versioned
  tree under /usr/lib64/llvm22 with -22 command links so it can be installed
  alongside llvm 23.
