Name:       sxhkd
Version:    0.6.3
Release:    1
Summary:    Simple X hotkey daemon
License:    BSD-2-Clause
URL:        https://github.com/baskerville/sxhkd
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: gcc, make, pkgconf
BuildRequires: libxcb, xcb-util-keysyms

%description
sxhkd is a simple X hotkey daemon: it reads a configuration file
describing key bindings and executes the associated commands.

%prep
%setup -q

%build
%make_build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} PREFIX=/usr

%files -f %{_sourcedir}/sxhkd.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.6.3-1
- Not in the base set; latest upstream stable 2026-11-05
  (tag 0.6.3).  Built with the upstream plain Makefile against
  libxcb and xcb-util-keysyms.
- Update from 0.6.1 to 0.6.3.
