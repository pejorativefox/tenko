Name:       xcb-util-renderutil
Version:    0.3.10
Release:    4
Summary:    XCB render utilities
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxcb-render-util
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
XCB render utilities

%prep
%setup -q

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xcb-util-renderutil.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.3.10-4
- Record the verified license (MIT): COPYING (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.3.10-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.3.10-1
- Version bump
