Name:       file
Version:    5.48
Release:    2
Summary:    A file type guesser
License:    BSD-2-Clause
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
A file type guesser

%prep
%setup -q 

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/file.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.48-2
- Record the verified license (BSD-2-Clause): COPYING (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 5.48
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 5.45
- Version bump
