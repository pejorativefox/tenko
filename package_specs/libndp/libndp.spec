Name:       libndp
Version:    1.9
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz


%description
TODO

%prep
%setup

%build
%configure  --sysconfdir=/etc    \
            --localstatedir=/var \
            --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/ndptool
/usr/include/ndp.h
/usr/lib64/libndp.so
/usr/lib64/libndp.so.0
/usr/lib64/libndp.so.0.3.0
/usr/lib64/pkgconfig/libndp.pc
/usr/share/man/man8/ndptool.8.gz

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.9-1
- Sync with BLFS r13.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.7-1
- Version bump

