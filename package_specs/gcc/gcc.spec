Name:       gcc
Version:    16.2.0
Release:    3
Summary:    The GNU Compiler Collection
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
Requires:   gcc-libs = %{version}-%{release}


%description
The GNU Compiler Collection includes front ends for C, C++, Objective-C, Fortran, Ada, Go, and D, as well as libraries for these languages


%prep
%setup -q


%build
export CFLAGS="-O2 -g"
export CXXFLAGS="-O2 -g"
export LDFLAGS=""
case $(uname -m) in
  x86_64)
    sed -e '/m64=/s/lib64/lib/' \
        -i.orig gcc/config/i386/t-linux64
  ;;
esac

mkdir -v build

echo "MULTILIB_OSDIRNAMES = m64=../lib64" >> gcc/config/i386/t-linux64

pushd build
../configure --prefix=/usr            \
             LD=ld                    \
             --enable-languages=c,c++ \
             --enable-default-pie     \
             --enable-default-ssp     \
             --enable-host-pie        \
             --enable-targets=all     \
             --disable-multilib       \
             --disable-bootstrap      \
             --disable-fixincludes    \
             --with-system-zlib       \
             --libdir=%{_libdir}
%make_build
popd


%install
rm -rf %{buildroot}
pushd build
%make_install
popd
rm -vf %{buildroot}%{_infodir}/dir*
ln -sfv gcc %{buildroot}/usr/bin/cc


%package libs
Summary:    GCC runtime libraries
License:    GPL3

%description libs
The GCC runtime support libraries: libgcc_s, libstdc++, libatomic, libgomp,
libquadmath, libitm, libasan, libhwasan, liblsan, libtsan, libubsan, libssp
and libcc1.  The compiler in gcc requires this package; runtime-only installs
can use it without pulling the compiler.

%files -f %{_sourcedir}/gcc.filelist
%files libs -f %{_sourcedir}/gcc-libs.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 16.2.0-3
- Split the runtime libraries into gcc-libs; gcc requires it (size audit P0)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 16.2.0
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 16.2.0
- Sync with LFS r13.1

* Sun Sep 3 2023 Chris Statzer <chris.statzer@gmail.com> 13.2.0
- Version bump

* Thu May 15 2020 Chris Statzer <chris.statzer@qq.com> 8.2.0-3
- Cleaned up spec file and added libgcc, libstdc++ subpackages to clean up the deps of many packages.
