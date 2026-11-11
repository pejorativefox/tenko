Name:       libtool
Version:    2.6.2
Release:    2
Summary:    Generic library support script
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Generic library support script

%prep
%setup -q

%build
%configure
# keep pre-generated man pages; help2man is not in the seed
touch doc/libtool.1 doc/libtoolize.1
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libtool.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.6.2-2
- Record the verified license (GPL-2.0-or-later AND LGPL-2.1-or-later): COPYING, libltdl/COPYING.LIB (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.6.2
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 2.4.7-1
- Version bump
