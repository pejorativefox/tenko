Name:       findutils
Version:    4.11.0
Release:    3
Summary:    GNU find utilities
License:    GPL-3.0-or-later
URL:        https://www.gnu.org/software/findutils/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The GNU Find Utilities are the basic directory searching utilities of the GNU operating system.

%package lang
Summary:    findutils translations
Requires:   findutils = %{version}-%{release}

%description lang
Translations for findutils.

%prep
%setup -q

%build
%configure --without-selinux 
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/findutils.filelist
%files lang -f %{_sourcedir}/findutils-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.11.0-3
- Record the verified license (GPL-3.0-or-later): find/defs.h (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.11.0-2
- Split lang payload into findutils-lang (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.11.0
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 4.9.0-1
- Version bump
