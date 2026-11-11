Name:       gawk
Version:    5.4.1
Release:    3
Summary:    GNU pattern scanner
License:    GPL-3.0-or-later
URL:        https://www.gnu.org/software/gawk/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

Provides: /bin/gawk

%description
Gawk is a powerful text-processing and data-manipulating tool

%package lang
Summary:    gawk translations
Requires:   gawk = %{version}-%{release}

%description lang
Translations for gawk.

%package doc
Summary:    gawk documentation
Requires:   gawk = %{version}-%{release}

%description doc
Documentation for gawk.

%prep
%setup -q

%build
sed -i 's/extras//' Makefile.in
%configure 
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/gawk.filelist
%files lang -f %{_sourcedir}/gawk-lang.filelist
%files doc -f %{_sourcedir}/gawk-doc.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.4.1-3
- Record the verified license (GPL-3.0-or-later): awk.h (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 5.4.1-2
- Split lang, doc payload into gawk-lang, gawk-doc (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 5.4.1
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 5.2.2-1
- Version bump
