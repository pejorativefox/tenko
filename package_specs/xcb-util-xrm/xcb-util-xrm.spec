Name:       xcb-util-xrm
Version:    1.3
Release:    4
Summary:    XCB utility functions for the X resource manager
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

%description
The XCB util-xrm module provides utility functions for the X resource
manager. It sits on top of libxcb and makes the raw X protocol more
convenient to use.

%prep
%setup -q

%build
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xcb-util-xrm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.3-4
- Replace the TODO summary/description and record the verified license
  (MIT): COPYING (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.3-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

# let's skip this for now

