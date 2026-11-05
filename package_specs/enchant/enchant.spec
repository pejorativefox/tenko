Name:       enchant
Version:    2.8.21
Release:    2
Summary:    Spell check library
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Spell check library

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/bin/enchant-2
/usr/bin/enchant-lsmod-2
/usr/include/enchant-2/enchant++.h
/usr/include/enchant-2/enchant.h
/usr/lib64/enchant-2/enchant_aspell.so
/usr/lib64/libenchant-2.a
/usr/lib64/libenchant-2.so
/usr/lib64/libenchant-2.so.2
/usr/lib64/libenchant-2.so.2.8.21
/usr/lib64/pkgconfig/enchant-2.pc
/usr/share/doc/enchant/enchant-2.html
/usr/share/doc/enchant/enchant-lsmod-2.html
/usr/share/doc/enchant/enchant.html
/usr/share/enchant-2/enchant.ordering
/usr/share/man/man1/enchant-2.1.gz
/usr/share/man/man1/enchant-lsmod-2.1.gz
/usr/share/man/man5/enchant.5.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.8.21-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING.LIB and src/enchant.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.8.21-1
- Sync with BLFS r13.1

* Wed Sep 09 2020 Chris Statzer <chris.statzer@qq.com> 2.2.11
- Initial RPM

