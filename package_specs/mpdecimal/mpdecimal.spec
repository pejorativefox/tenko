Name:       mpdecimal
Version:    4.0.1
Release:    1
Summary:    Decimal floating point library
License:    BSD
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
libmpdec is a library for arbitrary precision correctly rounded decimal
floating point arithmetic.

%prep
%setup -q

%build
%configure --disable-static --docdir=%{_docdir}/%{name}-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/include/
/usr/lib64/libmpdec*.so*
/usr/lib64/pkgconfig/
/usr/share/doc/%{name}-%{version}/
/usr/share/man/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.0.1
- Initial package (LFS r13.1)
