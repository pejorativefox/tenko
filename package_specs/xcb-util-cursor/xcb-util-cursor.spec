Name:       xcb-util-cursor
Version:    0.1.6
Release:    4
Summary:    XCB cursor utilities
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxcb-cursor
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
XCB cursor utilities

%prep
%setup -q

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xcb-util-cursor.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.1.6-4
- Record the verified license (MIT): COPYING (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.1.6-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.1.6-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.1.4-1
- Version bump
