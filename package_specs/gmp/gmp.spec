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
# gcc-15+ compatibility (LFS r13.1)
sed -i '/long long t1;/,+1s/()/(...)/' configure
%configure --enable-cxx --disable-static --docdir=/usr/share/doc/gmp-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/include/gmp.h
/usr/include/gmpxx.h
/usr/lib64/libgmp.so
/usr/lib64/libgmp.so.10
/usr/lib64/libgmp.so.10.5.0
/usr/lib64/libgmpxx.so
/usr/lib64/libgmpxx.so.4
/usr/lib64/libgmpxx.so.4.7.0
/usr/lib64/pkgconfig/gmp.pc
/usr/lib64/pkgconfig/gmpxx.pc
/usr/share/info/gmp.info-1.gz
/usr/share/info/gmp.info-2.gz
/usr/share/info/gmp.info.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 6.3.0-2
- Record the verified license (LGPL-3.0-or-later OR GPL-2.0-or-later): README and COPYING (issue #8).

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 6.3.0
- Version bump
