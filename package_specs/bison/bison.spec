Name:       bison
Version:    3.8.2
Release:    3
Summary:    GNU parser generator
License:    GPL-3.0-or-later
URL:        https://www.gnu.org/software/bison/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
GNU parser generator

%package lang
Summary:    bison translations
Requires:   bison = %{version}-%{release}

%description lang
Translations for bison.

%package doc
Summary:    bison documentation
Requires:   bison = %{version}-%{release}

%description doc
Documentation for bison.

%prep
%setup -q

%build
%configure --docdir=/usr/share/doc/bison-%{version}
# keep the shipped man page; the help2man rule is fragile in rpmbuild
touch doc/bison.1
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*


%files -f %{_sourcedir}/bison.filelist
%files lang -f %{_sourcedir}/bison-lang.filelist
%files doc -f %{_sourcedir}/bison-doc.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.8.2-3
- Record the verified license (GPL-3.0-or-later): src/main.c (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.8.2-2
- Split lang, doc payload into bison-lang, bison-doc (size audit)

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 3.8.2-1
- Version bump
