Name:       binutils
Version:    2.47
Release:    1
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

%files -f %{_sourcedir}/binutils.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.47
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.47
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 2.41
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 2.32
- Initial RPM
