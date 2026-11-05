Name:       kbd
Version:    2.10.0
Release:    3
Summary:    Utilities for managing Linux console
License:    GPL-2.0-or-later AND LGPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Patch:      kbd-2.10.0-backspace-1.patch
Prefix:     /usr

%description
The kbd project contains utilities for managing Linux console (Linux console, virtual terminals, keyboard, etc.) – mainly, what they do is loading console fonts and keyboard maps.

%package lang
Summary:    kbd translations
Requires:   kbd = %{version}-%{release}

%description lang
Translations for kbd.

%prep
%setup -q 
patch -Np1 -i %{_sourcedir}/kbd-2.10.0-backspace-1.patch

%build
sed -i 's/\(RESIZECONS_PROGS=\)yes/\1no/g' configure
sed -i 's/resizecons.8 //' docs/man/man8/Makefile.in

%configure --disable-vlock --disable-xkb
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/kbd.filelist
%files lang -f %{_sourcedir}/kbd-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.10.0-3
- Record the verified license (GPL-2.0-or-later AND LGPL-2.0-or-later): README and src/include/keymap.h (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.10.0-2
- Split lang payload into kbd-lang (size audit)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.10.0
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 2.6.1-1
- Version bump
