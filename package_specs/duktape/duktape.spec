Name:       duktape
Version:    2.7.0
Release:    1
Summary:    Embeddable JavaScript engine
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
Duktape is an embeddable JavaScript engine with a compact footprint.

%prep
%setup -q

%build
sed -i 's/-Os/-O2/' Makefile.sharedlibrary
make -f Makefile.sharedlibrary INSTALL_PREFIX=/usr

%install
rm -rf %{buildroot}
make -f Makefile.sharedlibrary INSTALL_PREFIX=%{buildroot}/usr install

%files
/usr/

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.7.0
- Initial package (BLFS r13.1)
