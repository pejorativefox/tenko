Name:       xcb-util-cursor
Version:    0.1.6
Release:    1
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
* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.1.6-1
- Sync with BLFS r13.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.1.4-1
- Version bump
