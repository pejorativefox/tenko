Name:       less
Version:    710
Release:    2
Summary:    open-source file pager. 
License:    GPL-3.0-or-later OR BSD-2-Clause
URL:        https://www.greenwoodsoftware.com/less/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Less is a free, open-source file pager. 

%prep
%setup -q

%build

%configure 
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/less.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 710-2
- Record the verified license (GPL-3.0-or-later OR BSD-2-Clause): README and LICENSE (issue #8).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 710-1
- Update to 710 (current upstream version).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 704
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 643-1
 Version bump
