Name:       binutils
Version:    2.47
Release:    2
Summary:    GNU binutils
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
%description
TODO

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

%package devel
Summary:    binutils development headers, static libraries and linker stubs
License:    GPL3
Requires:   binutils = %{version}-%{release}

%description devel
Headers and static/shared linker files for BFD, opcodes, libctf, libsframe
and libiberty.  Required to build programs that link against the binutils
libraries; the binutils tools package remains usable without it.

%package lang
Summary:    binutils translations
License:    GPL3
Supplements: binutils = %{version}-%{release}

%description lang
Translations for the binutils tools, bfd, gas, gprof, ld and opcodes.

%package doc
Summary:    binutils documentation
License:    GPL3
Supplements: binutils = %{version}-%{release}

%description doc
Info and man pages for the binutils tools.

%files -f %{_sourcedir}/binutils.filelist
%files devel -f %{_sourcedir}/binutils-devel.filelist
%files lang -f %{_sourcedir}/binutils-lang.filelist
%files doc -f %{_sourcedir}/binutils-doc.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.47-2
- Split development files, translations and documentation into subpackages
  (packaging only; versions unchanged)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.47
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.47
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 2.41
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 2.32
- Initial RPM
