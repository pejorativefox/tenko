Name:       xcb-util-wm
Version:    0.4.2
Release:    4
Summary:    XCB window manager utilities
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
XCB window manager utilities

%prep
%setup -q

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xcb-util-wm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.4.2-4
- Record the verified license (MIT): COPYING (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.4.2-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.4.2-1
- Version bump
