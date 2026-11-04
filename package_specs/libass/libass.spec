Name:       libass
Version:    0.17.5
Release:    1
Summary:    TODO
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
TODO

%prep
%setup -q -a0

%build
%configure --prefix=/usr --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/include/ass/ass.h
/usr/include/ass/ass_types.h
/usr/lib64/libass.so
/usr/lib64/libass.so.9
/usr/lib64/libass.so.9.4.2
/usr/lib64/pkgconfig/libass.pc

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.17.5-1
- Sync with BLFS r13.1

# let's skip this for now
