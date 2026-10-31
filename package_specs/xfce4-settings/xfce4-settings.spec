Name:       xfce4-settings
Version:    4.20.5
Release:    1
Summary:    Settings manager of the Xfce desktop
License:    GPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Settings manager of the Xfce desktop

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/bin
/usr/etc/xdg/
/usr/lib64/
/usr/share/

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.5
- Sync with BLFS r13.1 (4.19.0)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

