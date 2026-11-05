Name:       psmisc
Version:    23.7
Release:    3
Summary:    procfs tools
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
This package contains miscellaneous utilities that use the proc file-system.

%package lang
Summary:    psmisc translations
Requires:   psmisc = %{version}-%{release}

%description lang
Translations for psmisc.

%prep
%setup -q

%build
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*


%files -f %{_sourcedir}/psmisc.filelist
%files lang -f %{_sourcedir}/psmisc-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 23.7-3
- Record the verified license (GPL-2.0-or-later): src/fuser.c (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 23.7-2
- Split lang payload into psmisc-lang (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 23.7
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump
