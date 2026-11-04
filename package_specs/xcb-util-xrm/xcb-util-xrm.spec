Name:       xcb-util-xrm
Version:    1.3
Release:    3
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

%description
TODO

%package devel
Summary:    Development files for xcb-util-xrm
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in xcb-util-xrm; this empty package only
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
/usr/include/xcb/xcb_xrm.h
/usr/lib64/libxcb-xrm.a
/usr/lib64/libxcb-xrm.so
/usr/lib64/libxcb-xrm.so.0
/usr/lib64/libxcb-xrm.so.0.0.0
/usr/lib64/pkgconfig/xcb-xrm.pc
%files devel

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.3-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

# let's skip this for now

