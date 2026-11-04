Name:       giflib
Version:    6.1.3
Release:    1
Summary:    Library for loading and manipulationg GIF images
License:    GPL
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The giflib package contains libraries for reading and writing GIFs as well as programs for converting and working with GIF files. 

%prep
%setup

%build
%make_build 

%install
rm -rf %{buildroot}
make install PREFIX=%{buildroot}/usr

%files
/usr/bin/gifbuild
/usr/bin/gifclrmp
/usr/bin/giffix
/usr/bin/giftext
/usr/bin/giftool
/usr/include/gif_lib.h
/usr/lib/libgif.a
/usr/lib/libgif.so
/usr/lib/libgif.so.7
/usr/lib/libgif.so.7.2.0
/usr/share/doc/giflib/html/gif2rgb.html
/usr/share/doc/giflib/html/gif_lib.html
/usr/share/doc/giflib/html/gifbg.html
/usr/share/doc/giflib/html/gifbuild.html
/usr/share/doc/giflib/html/gifclrmp.html
/usr/share/doc/giflib/html/gifcolor.html
/usr/share/doc/giflib/html/gifecho.html
/usr/share/doc/giflib/html/giffilter.html
/usr/share/doc/giflib/html/giffix.html
/usr/share/doc/giflib/html/gifhisto.html
/usr/share/doc/giflib/html/gifinto.html
/usr/share/doc/giflib/html/giflib-logo.gif
/usr/share/doc/giflib/html/giflib.html
/usr/share/doc/giflib/html/gifsponge.html
/usr/share/doc/giflib/html/giftext.html
/usr/share/doc/giflib/html/giftool.html
/usr/share/doc/giflib/html/gifwedge.html
/usr/share/doc/giflib/html/index.html
/usr/share/doc/giflib/html/intro.html
/usr/share/man/man1/gifbuild.1.gz
/usr/share/man/man1/gifclrmp.1.gz
/usr/share/man/man1/giffix.1.gz
/usr/share/man/man1/giftext.1.gz
/usr/share/man/man1/giftool.1.gz
/usr/share/man/man7/giflib.7.gz

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 6.1.3-1
- Sync with BLFS r13.1

* Wed Aug 19 2020 Chris Statzer <chris.statzer@qq.com> 5.2.1
- Initial RPM

