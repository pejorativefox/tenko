Name:       mpc
Version:    1.4.1
Release:    2
Summary:    Complex floating-point library with exact rounding
License:    LGPL-3.0-or-later
Source0:    mpc-1.4.1.tar.xz
Prefix:     /usr

%description
GNU MPC is a complex floating-point library with exact rounding. It is based
on the GNU MPFR floating-point library, which is itself based on the GNU MP
library.

%prep
%setup -q

%build
%configure --disable-static --docdir=/usr/share/doc/mpc-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/include/mpc.h
/usr/lib64/libmpc.so
/usr/lib64/libmpc.so.3
/usr/lib64/libmpc.so.3.4.1
/usr/lib64/pkgconfig/mpc.pc
/usr/share/info/mpc.info.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.4.1-2
- Replace the TODO summary/description and record the verified license
  (LGPL-3.0-or-later): src/abs.c (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.4.1
- Sync with the base set

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 1.3.1
- Version bump
