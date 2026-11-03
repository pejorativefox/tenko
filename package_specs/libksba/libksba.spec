Name:       libksba
Version:    1.8.1
Release:    1
Summary:    X.509 certificate library
License:    GPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
X.509 certificate library

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
/usr/include/ksba.h
/usr/lib64/libksba.so
/usr/lib64/libksba.so.8
/usr/lib64/libksba.so.8.16.1
/usr/lib64/pkgconfig/ksba.pc
/usr/share/aclocal/ksba.m4
/usr/share/info/ksba.info.gz

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.8.1-1
- Sync with BLFS r13.1

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.3.5
- Initial RPM

