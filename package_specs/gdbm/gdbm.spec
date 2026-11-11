Name:       gdbm
Version:    1.26
Release:    2
Summary:    GNU database library
License:    GPL-3.0-or-later
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

%files -f %{_sourcedir}/gdbm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.26-2
- Record the verified license (GPL-3.0-or-later): src/gdbmopen.c (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.26
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.3-1
- Version bump
