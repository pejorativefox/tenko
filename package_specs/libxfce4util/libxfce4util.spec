Name:       libxfce4util
Version:    4.20.1
Release:    1
Summary:    Basic utility library for Xfce4.
License:    GPL
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Basic utility library for Xfce4.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/libxfce4util.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.1
- Sync with BLFS r13.1 (4.19.2)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.2
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

