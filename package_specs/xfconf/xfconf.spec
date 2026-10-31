Name:       xfconf
Version:    4.20.0
Release:    1
Summary:    Flexible, easy-to-use configuration management system
License:    GPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Flexible, easy-to-use configuration management system

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/bin/
/usr/include/
/usr/lib64/
/usr/share/

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with BLFS r13.1 (4.19.0)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.1
- Initial RPM

