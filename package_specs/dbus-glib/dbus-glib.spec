Name:       dbus-glib
Version:    0.116
Release:    2
Summary:    D-Bus bindings for GLib
License:    AFL-2.1 OR GPL-2.0-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz


%description
dbus-glib is a deprecated D-Bus binding for GLib. It receives minimal
maintenance and security fixes for projects such as Telepathy and
NetworkManager that still rely on it; new projects should use GDBus.

%prep
%setup -a 0

%build
%configure --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/dbus-binding-tool
/usr/include/dbus-1.0/dbus/dbus-glib-bindings.h
/usr/include/dbus-1.0/dbus/dbus-glib-lowlevel.h
/usr/include/dbus-1.0/dbus/dbus-glib.h
/usr/include/dbus-1.0/dbus/dbus-gtype-specialized.h
/usr/include/dbus-1.0/dbus/dbus-gvalue-parse-variant.h
/usr/lib64/libdbus-glib-1.so
/usr/lib64/libdbus-glib-1.so.2
/usr/lib64/libdbus-glib-1.so.2.3.7
/usr/lib64/pkgconfig/dbus-glib-1.pc
/usr/share/gtk-doc/html/dbus-glib/api-index-full.html
/usr/share/gtk-doc/html/dbus-glib/ch01.html
/usr/share/gtk-doc/html/dbus-glib/ch02.html
/usr/share/gtk-doc/html/dbus-glib/ch03.html
/usr/share/gtk-doc/html/dbus-glib/dbus-binding-tool.html
/usr/share/gtk-doc/html/dbus-glib/dbus-glib-DBus-GLib-low-level.html
/usr/share/gtk-doc/html/dbus-glib/dbus-glib-DBus-GObject-related-functions.html
/usr/share/gtk-doc/html/dbus-glib/dbus-glib-DBusGConnection.html
/usr/share/gtk-doc/html/dbus-glib/dbus-glib-DBusGError.html
/usr/share/gtk-doc/html/dbus-glib/dbus-glib-DBusGMessage.html
/usr/share/gtk-doc/html/dbus-glib/dbus-glib-DBusGMethod.html
/usr/share/gtk-doc/html/dbus-glib/dbus-glib-DBusGProxy.html
/usr/share/gtk-doc/html/dbus-glib/dbus-glib-Specializable-GType-System.html
/usr/share/gtk-doc/html/dbus-glib/dbus-glib.devhelp2
/usr/share/gtk-doc/html/dbus-glib/home.png
/usr/share/gtk-doc/html/dbus-glib/index.html
/usr/share/gtk-doc/html/dbus-glib/left-insensitive.png
/usr/share/gtk-doc/html/dbus-glib/left.png
/usr/share/gtk-doc/html/dbus-glib/right-insensitive.png
/usr/share/gtk-doc/html/dbus-glib/right.png
/usr/share/gtk-doc/html/dbus-glib/style.css
/usr/share/gtk-doc/html/dbus-glib/up-insensitive.png
/usr/share/gtk-doc/html/dbus-glib/up.png
/usr/share/man/man1/dbus-binding-tool.1.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.116-2
- Replace the TODO summary/description and record the verified license
  (AFL-2.1 OR GPL-2.0-or-later): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.116-1
- Sync with BLFS r13.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.11.0-1
- Version bump

