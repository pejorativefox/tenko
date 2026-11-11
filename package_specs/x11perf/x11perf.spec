Name:       x11perf
Version:    1.6.1
Release:    2
Summary:    X11 server performance test program
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/test/x11perf
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2



%description
The x11perf program runs one or more performance tests and reports how fast
an X server can execute the tests. It covers graphics operations as well as
window management operations such as creating, mapping and moving windows.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/x11perf.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.6.1-2
- Replace the TODO summary/description and record the verified license
  (MIT): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.6.1-1
- Update to x11perf 1.6.1, the latest published x.org release
  (1.6.2 does not exist). Not in the base set (x.org archive-era
  tool); latest upstream stable 2026-11-05.
