Name:       fribidi
Version:    1.0.18
Release:    4
Summary:    GNU FriBidi 
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
Provides: pkgconfig(fribidi)

%description
The Free Implementation of the Unicode Bidirectional Algorithm.

%prep
%setup -q

%build
mkdir build-glib
pushd build-glib

meson --prefix=/usr ..
ninja
popd

%install    
rm -rf %{buildroot}
pushd build-glib
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/fribidi.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.18-4
- Record the verified license (LGPL-2.1-or-later): COPYING (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.0.18-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Mon Nov  2 2026 browneye <build@browneye.invalid> 1.0.18-1
- Update to 1.0.18 (current LFS/BLFS r13.1 trunk version).

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.0.16
- Sync with BLFS r13.1 (1.0.13)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.0.13-1
- Version bump
