Name:       xfce4-power-manager
Version:    4.20.1
Release:    1
Summary:    Power manager for Xfce desktop
License:    GPL2
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Power manager for Xfce desktop

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfce4-power-manager.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.1
- Sync with BLFS r13.1 (4.19.1)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.6.5
- Initial RPM

