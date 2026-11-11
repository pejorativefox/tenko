Name:       npth
Version:    1.8
Release:    2
Summary:    POSIX/ANSI-C Scheduling library
License:    LGPL-2.1-or-later
URL:        https://gnupg.org/software/npth/
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
POSIX/ANSI-C Scheduling library

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/npth.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.8-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING.LIB, LGPL v2.1, plus src/npth.c "or any later version" (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.8-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.6
- Initial RPM

