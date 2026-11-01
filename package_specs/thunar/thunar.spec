Name:       thunar
Version:    4.20.10
Release:    1
Summary:    Modern file manager for Xfce
License:    GPL2
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Modern file manager for Xfce

%prep
%setup 

%build
sed -i 's/\tinstall-systemd_userDATA/\t/' Makefile.in
%configure --docdir=/usr/share/doc/thunar-%{version}
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/thunar.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.9
- Sync with BLFS r13.1 (4.18.6)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.18.6
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.8.9
- Initial RPM

