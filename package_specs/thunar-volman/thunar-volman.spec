Name:       thunar-volman
Version:    4.20.0
Release:    3
Summary:    Automatic management of removeable devices in Thunar
License:    GPL-2.0-or-later
URL:        https://docs.xfce.org/xfce/thunar/thunar-volman
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Automatic management of removeable devices in Thunar

%package lang
Summary:    thunar-volman translations
Requires:   thunar-volman = %{version}-%{release}

%description lang
Translations for thunar-volman.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/thunar-volman.filelist
%files lang -f %{_sourcedir}/thunar-volman-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.0-3
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.0-2
- Split lang payload into thunar-volman-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with 4.18.0

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.18.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.9.5
- Initial RPM

