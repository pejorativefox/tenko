Name:       xcb-util-wm
Version:    0.4.2
Release:    3
Summary:    XCB window manager utilities
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
XCB window manager utilities

%package devel
Summary:    Development files for xcb-util-wm
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in xcb-util-wm; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

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
/usr/include/xcb/xcb_ewmh.h
/usr/include/xcb/xcb_icccm.h
/usr/lib64/libxcb-ewmh.a
/usr/lib64/libxcb-ewmh.so
/usr/lib64/libxcb-ewmh.so.2
/usr/lib64/libxcb-ewmh.so.2.0.0
/usr/lib64/libxcb-icccm.a
/usr/lib64/libxcb-icccm.so
/usr/lib64/libxcb-icccm.so.4
/usr/lib64/libxcb-icccm.so.4.0.0
/usr/lib64/pkgconfig/xcb-ewmh.pc
/usr/lib64/pkgconfig/xcb-icccm.pc
%files devel



%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.4.2-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.4.2-1
- Version bump
