Name:       xfce4-appfinder
Version:    4.20.0
Release:    3
Summary:    An application finder for Xfce
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
An application finder for Xfce

%package lang
Summary:    xfce4-appfinder translations
Requires:   xfce4-appfinder = %{version}-%{release}

%description lang
Translations for xfce4-appfinder.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfce4-appfinder.filelist
%files lang -f %{_sourcedir}/xfce4-appfinder-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.0-3
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.0-2
- Split lang payload into xfce4-appfinder-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with BLFS r13.1 (4.19.0)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

