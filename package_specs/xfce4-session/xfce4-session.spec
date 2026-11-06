Name:       xfce4-session
Version:    4.20.4
Release:    3
Summary:    A session manager for Xfce
License:    GPL-2.0-or-later AND GPL-2.0-only
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: iceauth

%description
A session manager for Xfce

%package lang
Summary:    xfce4-session translations
Requires:   xfce4-session = %{version}-%{release}

%description lang
Translations for xfce4-session.

%prep
%setup

%build
%configure --disable-legacy-sm
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfce4-session.filelist
%files lang -f %{_sourcedir}/xfce4-session-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.4-3
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND GPL-2.0-only): COPYING (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.4-2
- Split lang payload into xfce4-session-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.4
- Sync with 4.19.1

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

