Name:       expat
Version:    2.8.3
Release:    1
Summary:    stream-oriented XML parser
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
stream-oriented XML parser

%prep
%setup -q

%build
%configure --disable-static \
           --docdir=/usr/share/doc/expat-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/xmlwf
/usr/include/expat.h
/usr/include/expat_config.h
/usr/include/expat_external.h
/usr/lib64/cmake/expat-%{version}/
/usr/lib64/libexpat.so.1.12.3
/usr/lib64/libexpat.so
/usr/lib64/libexpat.so.1
/usr/lib64/pkgconfig/expat.pc
/usr/share/doc/expat-%{version}/
/usr/share/man/man1/xmlwf.1.gz

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.8.3
- Sync with LFS r13.1

# let's skip this for now
