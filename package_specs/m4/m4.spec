Name:       m4
Version:    1.4.21
Release:    4
Summary:    M4 macro processor
License:    GPL-3.0-or-later
URL:        https://www.gnu.org/software/m4/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
GNU m4 is an implementation of the traditional Unix macro processor. It is
mostly SVR4 compatible and includes built-in functions for including files,
running shell commands and doing arithmetic.

%package lang
Summary:    m4 translations
Requires:   m4 = %{version}-%{release}

%description lang
Translations for m4.

%prep
%setup -q -a0

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/m4.filelist
%files lang -f %{_sourcedir}/m4-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.4.21-4
- Bump the release so the rebuilt licence metadata supersedes the
  previously published 1.4.21-3 RPM (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.4.21-3
- Replace the TODO summary/description and record the verified license
  (GPL-3.0-or-later): src/m4.c (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.4.21-2
- Split lang payload into m4-lang (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.4.21
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.4.19
- Version bump
