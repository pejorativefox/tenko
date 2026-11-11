Name:       libpipeline
Version:    1.5.8
Release:    2
Summary:    Subprocess manipulation library
License:    GPL-3.0-or-later
URL:        https://libpipeline.gitlab.io/libpipeline/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
C library for manipulating pipelines of subprocesses

%prep
%setup -q -a0

%build
%configure 
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libpipeline.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.5.8-2
- Record the verified license (GPL-3.0-or-later): README.md (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.5.8
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.7-1
- Version bump
