Name:       thunar-volman
Version:    4.20.0
Release:    1
Summary:    Automatic management of removeable devices in Thunar
License:    GPL2
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Automatic management of removeable devices in Thunar

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/bin/thunar-volman
/usr/bin/thunar-volman-settings
/usr/share/

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with BLFS r13.1 (4.18.0)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.18.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.9.5
- Initial RPM

