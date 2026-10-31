Name:       exo
Version:    4.20.0
Release:    1
Summary:    Application library for Xfce
License:    GPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Application library for Xfce

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/exo.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with BLFS r13.1 (4.18.0)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.18.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.12.8
- Initial RPM

