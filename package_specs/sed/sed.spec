Name:       sed
Version:    4.10
Release:    3
Summary:    The sed stream editor
License:    GPL-3.0-or-later
URL:        https://www.gnu.org/software/sed/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
sed (stream editor) is a non-interactive command-line text editor. 

%package lang
Summary:    sed translations
Requires:   sed = %{version}-%{release}

%description lang
Translations for sed.

%prep
%setup -q

%build
%configure --without-selinux
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*


%files -f %{_sourcedir}/sed.filelist
%files lang -f %{_sourcedir}/sed-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.10-3
- Record the verified license (GPL-3.0-or-later): sed/compile.c (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.10-2
- Split lang payload into sed-lang (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.10
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump
