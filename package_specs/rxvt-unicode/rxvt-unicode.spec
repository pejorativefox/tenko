Name:       rxvt-unicode
Version:    9.31
Release:    2
Summary:    rxvt-unicode is a fork of the well known terminal emulator rxvt.
License:    GPL-3.0-or-later AND (BSD-2-Clause OR GPL-2.0-or-later)
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
rxvt-unicode is a fork of the well known terminal emulator rxvt.

%prep
%setup

%build
sed '/interpolation/,+7d' -i src/rxvtutil.h
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/rxvt-unicode.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 9.31-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-3.0-or-later AND (BSD-2-Clause OR GPL-2.0-or-later)): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 9.31-1
- Sync with the base set

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 9.22-1
- Initial RPM

