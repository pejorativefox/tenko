Name:       giflib
Version:    6.1.3
Release:    3
Summary:    Library for loading and manipulationg GIF images
License:    MIT
URL:        https://giflib.sourceforge.net/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The giflib package contains libraries for reading and writing GIFs as well as programs for converting and working with GIF files. 

%prep
%setup

%build
%make_build 

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} PREFIX=/usr LIBDIR=/usr/lib64

%files -f %{_sourcedir}/giflib.filelist

%changelog
* Thu Nov 12 2026 tenko <build@tenko.invalid> 6.1.3-3
- Install libgif.so and libgif.a in /usr/lib64.  The Makefile hard-codes
  LIBDIR to $(PREFIX)/lib, so the package put them in /usr/lib.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 6.1.3-2
- Replace the legacy short licence name with the verified SPDX expression
  (MIT): COPYING and the per-file SPDX headers (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 6.1.3-1
- Sync with the base set

* Wed Aug 19 2020 Chris Statzer <chris.statzer@qq.com> 5.2.1
- Initial RPM

