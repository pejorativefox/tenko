Name:       libmd
Version:    1.3.0
Release:    1
Summary:    Message digest library
License:    BSD
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Message digest library used by libbsd.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/include/
/usr/lib64/libmd.so*
/usr/lib64/pkgconfig/
/usr/share/man/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.3.0
- Bootstrap dependency for shadow/libbsd
