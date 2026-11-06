Name:       binutils
Version:    2.47
Release:    4
Summary:    GNU binutils
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
%description
The GNU binutils are utilities for working with binary files, either object
files or executables. They include the linkers ld and gold, the assembler
gas, the profilers gprof and gprofng, the disassembler objdump, and the bfd
and opcodes libraries.

%prep
%setup -q

%build
mkdir build
pushd build
../configure --prefix=/usr       \
             --sysconfdir=/etc   \
             --enable-ld=default \
             --enable-plugins    \
             --enable-shared     \
             --disable-werror    \
             --enable-64-bit-bfd \
             --enable-new-dtags  \
             --with-lib-path=/usr/lib64 \
             --enable-default-hash-style=gnu \
             --without-debuginfod \
             --disable-gprofng \
             --with-system-zlib  \
             --libdir=%{_libdir}
%make_build tooldir=/usr
popd

%install
pushd build
rm -rf %{buildroot}
%make_install tooldir=/usr
rm -vf %{buildroot}%{_infodir}/dir*
rm -fv %{buildroot}/usr/lib/lib{bfd,ctf,ctf-nobfd,gprofng,opcodes,sframe}.a
popd

%package lang
Summary:    binutils translations
License:    GPL-3.0-or-later
Supplements: binutils = %{version}-%{release}

%description lang
Translations for the binutils tools, bfd, gas, gprof, ld and opcodes.

%package doc
Summary:    binutils documentation
License:    GFDL-1.3-or-later
Supplements: binutils = %{version}-%{release}

%description doc
Info and man pages for the binutils tools.

%files -f %{_sourcedir}/binutils.filelist
%files lang -f %{_sourcedir}/binutils-lang.filelist
%files doc -f %{_sourcedir}/binutils-doc.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.47-4
- Replace the TODO summary/description and record the verified license
  (GPL-3.0-or-later): COPYING3 (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.47-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.47-2
- Split development files, translations and documentation into subpackages
  (packaging only; versions unchanged)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.47
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.47
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 2.41
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 2.32
- Initial RPM
