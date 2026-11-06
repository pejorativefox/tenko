Name:       patch
Version:    2.8.1
Release:    2
Summary:    GNU patch utility
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The Patch package contains a program for modifying or creating files by applying a patch file typically created by the diff program. 

%prep
%setup -q

%build
%configure 
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/patch
/usr/share/man/man1/patch.1.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.8.1-2
- Record the verified license (GPL-3.0-or-later): src/patch.c (issue #8).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 2.8.1-1
- Update to 2.8.1 (current upstream version).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.8
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 2.7.6-1
- Version bump
