Name:       attr
Version:    2.6.0
Release:    2
Summary:    Commands for Manipulating Filesystem Extended Attributes
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
URL:        https://savannah.nongnu.org/projects/attr/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Commands for Manipulating Filesystem Extended Attributes

%prep
%setup

%build
%configure  --disable-static  \
            --sysconfdir=/etc \
            --docdir=/usr/share/doc/attr-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/attr.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.6.0-2
- Record the verified license (GPL-2.0-or-later AND LGPL-2.1-or-later): doc/COPYING and configure.ac (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.6.0
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 2.4.48
- Initial RPM

