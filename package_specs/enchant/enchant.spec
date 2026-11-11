Name:       enchant
Version:    2.8.21
Release:    2
Summary:    Spell check library
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Spell check library

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/enchant.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.8.21-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING.LIB and src/enchant.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.8.21-1
- Sync with the base set

* Wed Sep 09 2020 Chris Statzer <chris.statzer@qq.com> 2.2.11
- Initial RPM

