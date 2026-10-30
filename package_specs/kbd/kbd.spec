Name:       kbd
Version:    2.10.0
Release:    1
Summary:    Utilities for managing Linux console
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Patch:      kbd-2.10.0-backspace-1.patch
Prefix:     /usr

%description
The kbd project contains utilities for managing Linux console (Linux console, virtual terminals, keyboard, etc.) – mainly, what they do is loading console fonts and keyboard maps.

%prep
%setup -q 
patch -Np1 -i %{_sourcedir}/kbd-2.10.0-backspace-1.patch

%build
sed -i 's/\(RESIZECONS_PROGS=\)yes/\1no/g' configure
sed -i 's/resizecons.8 //' docs/man/man8/Makefile.in

%configure --disable-vlock
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/kbd.filelist

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.10.0
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 2.6.1-1
- Version bump
