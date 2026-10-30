Name:       libbsd
Version:    0.12.2
Release:    1
Summary:    BSD compatibility library
License:    BSD
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
BSD compatibility library used by shadow (readpassphrase).

%prep
%setup -q

%build
%configure --disable-static --without-libbsd
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/include/
/usr/lib64/libbsd-ctor.a
/usr/lib64/libbsd.so*
/usr/lib64/pkgconfig/
/usr/share/man/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 0.12.2
- Bootstrap dependency for shadow
