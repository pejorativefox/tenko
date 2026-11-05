Name:       grep
Version:    3.12
Release:    3
Summary:    Text searching cli tool
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
grep is a command-line utility for searching plain-text data sets for lines that match a regular expression. 

%package lang
Summary:    grep translations
Requires:   grep = %{version}-%{release}

%description lang
Translations for grep.

%prep
%setup -q

%build
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/grep.filelist
%files lang -f %{_sourcedir}/grep-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.12-3
- Record the verified license (GPL-3.0-or-later): src/grep.c (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.12-2
- Split lang payload into grep-lang (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.12
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump
