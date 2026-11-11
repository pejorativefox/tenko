Name:       gmp
Version:    6.3.0
Release:    2
Summary:    The GMP math libraries
License:    LGPL-3.0-or-later OR GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Library for arbitrary precision arithmetic

%prep
%setup -q 

%build
# gcc-15+ compatibility
sed -i '/long long t1;/,+1s/()/(...)/' configure
%configure --enable-cxx --disable-static --docdir=/usr/share/doc/gmp-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/gmp.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 6.3.0-2
- Record the verified license (LGPL-3.0-or-later OR GPL-2.0-or-later): README and COPYING (issue #8).

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 6.3.0
- Version bump
