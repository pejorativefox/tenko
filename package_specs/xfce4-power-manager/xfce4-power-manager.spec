Name:       xfce4-power-manager
Version:    4.20.1
Release:    3
Summary:    Power manager for Xfce desktop
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Power manager for Xfce desktop

%package lang
Summary:    xfce4-power-manager translations
Requires:   xfce4-power-manager = %{version}-%{release}

%description lang
Translations for xfce4-power-manager.

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
%files lang -f %{_sourcedir}/xfce4-power-manager-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.1-3
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.1-2
- Split lang payload into xfce4-power-manager-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.1
- Sync with BLFS r13.1 (4.19.1)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.6.5
- Initial RPM

