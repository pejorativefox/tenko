Name:       mpfr
Version:    4.2.2
Release:    2
Summary:    Library for multiple-precision floating-point computation
License:    LGPL-3.0-or-later
URL:        https://www.mpfr.org/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Library for multiple-precision floating-point computation

%prep
%setup -q

%build
%configure --disable-static --enable-thread-safe --docdir=/usr/share/doc/mpfr-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/mpfr.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.2.2-2
- Record the verified license (LGPL-3.0-or-later): src/mpfr.h (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.2.2
- Sync with the base set

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.2.1
- Version bump
