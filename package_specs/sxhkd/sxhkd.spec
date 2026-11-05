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

%files
/usr/bin/sxhkd
/usr/share/doc/sxhkd/examples/background_shell/profile
/usr/share/doc/sxhkd/examples/background_shell/shell
/usr/share/doc/sxhkd/examples/background_shell/sxhkdrc
/usr/share/doc/sxhkd/examples/background_shell/xinitrc
/usr/share/doc/sxhkd/examples/notification/autostart
/usr/share/doc/sxhkd/examples/notification/pam_environment
/usr/share/doc/sxhkd/examples/notification/sxhkd_notify
/usr/share/doc/sxhkd/examples/notification/xinitrc
/usr/share/man/man1/sxhkd.1.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.6.3-1
- Not in the LFS/BLFS r13.1 book; latest upstream stable 2026-11-05
  (tag 0.6.3).  Built with the upstream plain Makefile against
  libxcb and xcb-util-keysyms.
- Update from 0.6.1 to 0.6.3.
