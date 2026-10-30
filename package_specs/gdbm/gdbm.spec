Name:       gdbm
Version:    1.26
Release:    1
Summary:    GNU database library
License:    GPL3
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
GNU dbm (or GDBM, for short) is a library of database functions that use extensible hashing and work similar to the standard UNIX dbm.

%prep
%setup -q

%build
%configure --disable-static \
           --enable-libgdbm-compat
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/gdbm_dump
/usr/bin/gdbm_load
/usr/bin/gdbmtool
/usr/include/dbm.h
/usr/include/gdbm.h
/usr/include/ndbm.h
/usr/lib64/libgdbm.so
/usr/lib64/libgdbm.so.6
/usr/lib64/libgdbm.so.6.0.0
/usr/lib64/libgdbm_compat.so
/usr/lib64/libgdbm_compat.so.4
/usr/lib64/libgdbm_compat.so.4.0.0
/usr/share/info/gdbm.info.gz
/usr/share/locale/
/usr/share/man/man1/gdbm_dump.1.gz
/usr/share/man/man1/gdbm_load.1.gz
/usr/share/man/man1/gdbmtool.1.gz
/usr/share/man/man3/gdbm.3.gz

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.26
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.3-1
- Version bump
