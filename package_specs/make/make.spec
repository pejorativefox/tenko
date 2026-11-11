Name:       make
Version:    4.4.1
Release:    3
Summary:    GNU make
License:    GPL-3.0-or-later
URL:        https://www.gnu.org/software/make/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The Make package contains a program for controlling the generation of executables and other non-source files of a package from source files.

%package lang
Summary:    make translations
Requires:   make = %{version}-%{release}

%description lang
Translations for make.

%prep
%setup -q

%build
%configure 
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/make.filelist
%files lang -f %{_sourcedir}/make-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.4.1-3
- Record the verified license (GPL-3.0-or-later): README (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.4.1-2
- Split lang payload into make-lang (size audit)

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump
