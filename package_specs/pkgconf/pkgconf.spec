Name:       pkgconf
Version:    3.0.5
Release:    1
Summary:    Successor to pkg-config
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Successor to pkg-config and contains a tool for passing the include path and/or library paths to build tools during the configure and make phases of package installations. 

%prep
%setup -q

%build
%configure  --disable-static           \
            --docdir=/usr/share/doc/pkgconf-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install

ln -sv pkgconf   %{buildroot}/usr/bin/pkg-config
ln -sv pkgconf.1 %{buildroot}/usr/share/man/man1/pkg-config.1

%files
/usr/bin/bomtool
/usr/bin/pccritic
/usr/bin/pkg-config
/usr/bin/pkgconf
/usr/bin/spdxtool
/usr/include/pkgconf/libpkgconf/bsdstubs.h
/usr/include/pkgconf/libpkgconf/iter.h
/usr/include/pkgconf/libpkgconf/libpkgconf-api.h
/usr/include/pkgconf/libpkgconf/libpkgconf.h
/usr/include/pkgconf/libpkgconf/stdinc.h
/usr/lib64/libpkgconf.so
/usr/lib64/libpkgconf.so.8
/usr/lib64/libpkgconf.so.8.0.0
/usr/lib64/pkgconfig/libpkgconf.pc
/usr/share/aclocal/pkg.m4
/usr/share/doc/pkgconf-%{version}/
/usr/share/man/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.0.5
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 2.0.1
- Initial rpm
