Name:       libxcrypt
Version:    4.5.2
Release:    2
Summary:    Password hashing library
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The Libxcrypt package contains a modern library for one-way hashing of passwords.

%prep
%setup -q

%build
%configure  --enable-hashes=strong,glibc \
            --enable-obsolete-api=no     \
            	--disable-static             \
            --disable-werror             \
            --disable-failure-tokens
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/include/crypt.h
/usr/lib64/libcrypt.so
/usr/lib64/libcrypt.so.2
/usr/lib64/libcrypt.so.2.0.0
/usr/lib64/pkgconfig/libcrypt.pc
/usr/lib64/pkgconfig/libxcrypt.pc
/usr/share/man/

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.5.2-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING.LIB, plus lib/crypt.c "either version 2.1 ... or any later version" (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.5.2
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Initial RPM

