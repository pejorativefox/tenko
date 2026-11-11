Name:       dbus-glib
Version:    0.116
Release:    3
Summary:    D-Bus bindings for GLib
License:    AFL-2.1 OR GPL-2.0-or-later
URL:        https://gitlab.freedesktop.org/dbus/dbus-glib
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz


%description
dbus-glib is a deprecated D-Bus binding for GLib. It receives minimal
maintenance and security fixes for projects such as Telepathy and
NetworkManager that still rely on it; new projects should use GDBus.

%prep
%setup -a 0

%build
%configure --disable-static --enable-bash-completion
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/dbus-glib.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 0.116-3
- Build with --enable-bash-completion and package the dbus-binding-tool
  completion helper again.  The old 0.110 build installed it under
  /usr/etc/bash_completion.d, where nothing loaded it; the configure
  sysconfdir now puts it in /etc/bash_completion.d.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.116-2
- Replace the TODO summary/description and record the verified license
  (AFL-2.1 OR GPL-2.0-or-later): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.116-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.11.0-1
- Version bump

