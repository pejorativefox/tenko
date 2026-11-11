Name:       gperf
Version:    3.3
Release:    2
Summary:    GNU hash function generator
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
GNU gperf is a perfect hash function generator.

%prep
%setup -q

%build
%configure --docdir=/usr/share/doc/gperf-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/gperf.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.3-2
- Record the verified license (GPL-3.0-or-later): src/main.cc (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.3
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 3.1
- Version bump
