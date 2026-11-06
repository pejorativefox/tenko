Name:       xfwm4
Version:    4.20.0
Release:    3
Summary:    Xfce's window manager
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Xfce's window manager

%package lang
Summary:    xfwm4 translations
Requires:   xfwm4 = %{version}-%{release}

%description lang
Translations for xfwm4.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfwm4.filelist
%files lang -f %{_sourcedir}/xfwm4-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.0-3
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.0-2
- Split lang payload into xfwm4-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with 4.18.0

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.18.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

