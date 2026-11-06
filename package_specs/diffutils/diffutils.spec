Name:       diffutils
Version:    3.12
Release:    3
Summary:    GNU file difference utilities
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
GNU Diffutils is a package of several programs related to finding differences between files.

%package lang
Summary:    diffutils translations
Requires:   diffutils = %{version}-%{release}

%description lang
Translations for diffutils.

%prep
%setup -q

%build
%configure 
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/diffutils.filelist
%files lang -f %{_sourcedir}/diffutils-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.12-3
- Record the verified license (GPL-3.0-or-later): src/diff.c (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.12-2
- Split lang payload into diffutils-lang (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.12
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 3.10-1
- Version bump
