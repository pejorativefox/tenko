Name:       acl
Version:    2.4.0
Release:    2
Summary:    Linux access control lists.
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The Acl package contains utilities to administer Access Control Lists, which are used to
define more fine-grained discretionary access rights for files and directories. 

%prep
%setup

%build
%configure --disable-static       \
           --libexecdir=/usr/lib  \
           --docdir=/usr/share/doc/acl-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/bin/chacl
/usr/bin/getfacl
/usr/bin/setfacl
/usr/include/acl/libacl.h
/usr/include/sys/acl.h
/usr/lib64/libacl.so
/usr/lib64/libacl.so.1
/usr/lib64/libacl.so.1.2.2400
/usr/lib64/pkgconfig/libacl.pc
/usr/share/doc/acl-%{version}/
/usr/share/locale/
/usr/share/man/

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.4.0-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND LGPL-2.1-or-later): doc/COPYING, doc/COPYING.LGPL and the per-file headers (issue #8).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.4.0
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 2.2.53
- Initial RPM release
