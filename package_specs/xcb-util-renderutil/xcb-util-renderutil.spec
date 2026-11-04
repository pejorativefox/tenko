Name:       xcb-util-renderutil
Version:    0.3.10
Release:    3
Summary:    XCB render utilities
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz



%description
XCB render utilities

%package devel
Summary:    Development files for xcb-util-renderutil
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in xcb-util-renderutil; this empty package only
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
/usr/include/xcb/xcb_renderutil.h
/usr/lib64/libxcb-render-util.a
/usr/lib64/libxcb-render-util.so
/usr/lib64/libxcb-render-util.so.0
/usr/lib64/libxcb-render-util.so.0.0.0
/usr/lib64/pkgconfig/xcb-renderutil.pc
%files devel


%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.3.10-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.3.10-1
- Version bump
