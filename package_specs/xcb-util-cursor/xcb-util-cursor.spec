Name:       xcb-util-cursor
Version:    0.1.6
Release:    3
Summary:    XCB cursor utilities
License:    GPL3
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

%files
/usr/include/xcb/xcb_cursor.h
/usr/lib64/libxcb-cursor.a
/usr/lib64/libxcb-cursor.so
/usr/lib64/libxcb-cursor.so.0
/usr/lib64/libxcb-cursor.so.0.0.0
/usr/lib64/pkgconfig/xcb-cursor.pc

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.1.6-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.1.6-1
- Sync with BLFS r13.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.1.4-1
- Version bump
