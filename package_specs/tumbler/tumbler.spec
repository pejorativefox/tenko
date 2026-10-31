Name:       tumbler
Version:    4.20.2
Release:    1
Summary:    D-Bus service for applications to request thumbnails
License:    GPL2
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
D-Bus service for applications to request thumbnails

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/etc/
/usr/include/
/usr/lib64/
/usr/share/
/usr/lib/systemd/user/

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.2
- Sync with BLFS r13.1 (4.19.0)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.2.7
- Initial RPM

