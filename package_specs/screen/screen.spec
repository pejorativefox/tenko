Name:       screen
Version:    5.0.2
Release:    1
Summary:    Screen is a full-screen window manager that multiplexes a physical terminal between several processes
License:    GPL3
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Screen is a full-screen window manager that multiplexes a physical terminal between several processes

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -rf %{buildroot}/usr/share/info/dir

%files
/usr/bin/screen
/usr/bin/screen-5.0.2
/usr/share/info/screen.info.gz
/usr/share/man/man1/screen.1.gz
/usr/share/screen/utf8encodings/01
/usr/share/screen/utf8encodings/02
/usr/share/screen/utf8encodings/03
/usr/share/screen/utf8encodings/04
/usr/share/screen/utf8encodings/18
/usr/share/screen/utf8encodings/19
/usr/share/screen/utf8encodings/a1
/usr/share/screen/utf8encodings/a3
/usr/share/screen/utf8encodings/bf
/usr/share/screen/utf8encodings/c2
/usr/share/screen/utf8encodings/c3
/usr/share/screen/utf8encodings/c4
/usr/share/screen/utf8encodings/c6
/usr/share/screen/utf8encodings/c7
/usr/share/screen/utf8encodings/c8
/usr/share/screen/utf8encodings/cc
/usr/share/screen/utf8encodings/cd
/usr/share/screen/utf8encodings/d6

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 5.0.2-1
- Sync with BLFS r13.1

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.8.0
- Initial RPM

