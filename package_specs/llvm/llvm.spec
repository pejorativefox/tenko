Name:       llvm
Version:    22.1.8
Release:    1
Summary:    The LLVM Project is a collection of modular and reusable compiler and toolchain technologies. 
License:    UIUC
Source0:    llvm-project-%{version}.src.tar.xz
Prefix:     /usr

%description
The LLVM Project is a collection of modular and reusable compiler and toolchain technologies. Despite its name, LLVM has little to do with traditional virtual machines. The name "LLVM" itself is not an acronym; it is the full name of the project.

%prep
%setup -q -n llvm-project-%{version}.src
patch -Np1 -i %{_sourcedir}/llvm-%{version}-upstream_fix-1.patch
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
      -D LLVM_TARGETS_TO_BUILD="host;AMDGPU"                \
      -D LLVM_ENABLE_PROJECTS=clang                         \
      -D LLVM_ENABLE_RUNTIMES=compiler-rt                   \
      -D LLVM_BINUTILS_INCDIR=/usr/include                  \
      -D LLVM_INCLUDE_BENCHMARKS=OFF                        \
      -D CLANG_DEFAULT_PIE_ON_LINUX=ON                      \
      -D CLANG_CONFIG_FILE_SYSTEM_DIR=/etc/clang            \
      -W no-author -G Ninja ..
ninja
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

%files -f %{_sourcedir}/llvm.filelist


%changelog
* Tue Jun 13 2023 Chris Statzer <chris.statzer@gmail.com> 16.0.5
- Initial RPM

