Name:       gcc
Version:    16.2.0
Release:    7
Summary:    The GNU Compiler Collection
License:    GPL-3.0-or-later WITH GCC-exception-3.1
URL:        https://gcc.gnu.org/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
Requires:   gcc-libs = %{version}-%{release}
Obsoletes:  gcc-lto < %{version}-%{release}
Provides:   gcc-lto = %{version}-%{release}
BuildRequires: texinfo

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
License:    GPL-3.0-or-later WITH GCC-exception-3.1

%description libs
The GCC runtime support libraries: libgcc_s, libstdc++, libatomic, libgomp,
libquadmath, libitm, libasan, libhwasan, liblsan, libtsan, libubsan, libssp
and libcc1.  The compiler in gcc requires this package; runtime-only installs
can use it without pulling the compiler.

%package lang
Summary:    GCC translations
License:    GPL-3.0-or-later
Supplements: gcc = %{version}-%{release}

%description lang
Translations for the GCC driver, cpplib and libstdc++ messages.

%package doc
Summary:    GCC documentation
License:    GFDL-1.3-or-later
Supplements: gcc = %{version}-%{release}

%description doc
Info and man pages for GCC, cpp, gcov, libgomp, libitm and libquadmath.

%files -f %{_sourcedir}/gcc.filelist
%files libs -f %{_sourcedir}/gcc-libs.filelist
%files lang -f %{_sourcedir}/gcc-lang.filelist
%files doc -f %{_sourcedir}/gcc-doc.filelist

%changelog
* Thu Nov 12 2026 browneye <build@browneye.invalid> 16.2.0-7
- Fold gcc-lto back into gcc: lto1, lto-wrapper, lto-dump and
  liblto_plugin.so now ship together.  Splitting the plugin from
  lto-wrapper made gcc pass an empty -plugin-opt when gcc-lto was not
  installed, which broke every -flto link and every Rust link through
  cc -fuse-ld=lld (issue #63).  The 16.2.0 sources are unchanged.
  gcc obsoletes and provides gcc-lto so the old subpackage is replaced
  on upgrade.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 16.2.0-6
- Record the verified license (GPL-3.0-or-later WITH GCC-exception-3.1): COPYING3, COPYING.RUNTIME and gcc/doc/cpp.texi (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 16.2.0-5
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 16.2.0-4
- Split LTO, development files, translations and documentation out of gcc
  (packaging only; versions unchanged)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 16.2.0-3
- Split the runtime libraries into gcc-libs; gcc requires it (size audit P0)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 16.2.0
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 16.2.0
- Sync with the base set

* Sun Sep 3 2023 Chris Statzer <chris.statzer@gmail.com> 13.2.0
- Version bump

* Thu May 15 2020 Chris Statzer <chris.statzer@qq.com> 8.2.0-3
- Cleaned up spec file and added libgcc, libstdc++ subpackages to clean up the deps of many packages.
