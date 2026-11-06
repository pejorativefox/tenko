Name:       libksba
Version:    1.8.1
Release:    2
Summary:    X.509 certificate library
License:    (LGPL-3.0-or-later OR GPL-2.0-or-later) AND GPL-3.0-or-later
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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.8.1-2
- Replace the legacy short licence name with the verified SPDX expression
  ((LGPL-3.0-or-later OR GPL-2.0-or-later) AND GPL-3.0-or-later): AUTHORS, src/asn1-func.c and doc/ksba.texi (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.8.1-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.3.5
- Initial RPM

