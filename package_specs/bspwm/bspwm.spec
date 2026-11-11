Name:       bspwm
Version:    0.9.12
Release:    1
Summary:    A tiling window manager based on binary space partitioning
License:    BSD-2-Clause
URL:        https://github.com/baskerville/bspwm
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: gcc, make, pkgconf
BuildRequires: libxcb, xcb-util, xcb-util-keysyms, xcb-util-wm

%description
bspwm is a tiling window manager that represents windows as the leaves
of a full binary tree.  It only responds to X events and messages it
receives on a dedicated socket; bspc is the client used to control it.

%prep
%setup -q

%build
%make_build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} PREFIX=/usr

%files -f %{_sourcedir}/bspwm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.9.12-1
- Not in the base set; latest upstream stable 2026-11-05
  (tag 0.9.12).  Built with the upstream plain Makefile against
  libxcb, xcb-util, xcb-util-keysyms and xcb-util-wm.
- Update from 0.9.9 to 0.9.12.
