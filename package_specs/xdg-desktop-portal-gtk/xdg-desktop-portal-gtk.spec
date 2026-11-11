Name:       xdg-desktop-portal-gtk
Version:    1.15.3
Release:    1
Summary:    GTK backend for xdg-desktop-portal
License:    LGPL-2.1-or-later
URL:        https://github.com/flatpak/xdg-desktop-portal-gtk
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

Requires:   xdg-desktop-portal
Requires:   gsettings-desktop-schemas
BuildRequires: gtk+, glib, xdg-desktop-portal
BuildRequires: fontconfig
BuildRequires: gdk-pixbuf

%description
The GTK implementation of the xdg-desktop-portal interfaces.  Flatpak
applications use the portal for file choosers, printing, notifications,
opening links and other desktop integration; without a backend those
requests fail.

The XFCE session already ships /usr/share/xdg-desktop-portal/xfce-portals.conf,
which selects this backend as the default.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                 \
      --prefix=/usr            \
      --buildtype=release      \
      -Dwallpaper=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/xdg-desktop-portal-gtk.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 1.15.3-1
- New package: the GTK portal backend.  xdg-desktop-portal was packaged
  without an implementation, so flatpak apps had no file chooser, print or
  OpenURI backend (issue #29).
- Version 1.15.3 is the current upstream stable release.
- The Wallpaper portal is disabled because it needs gnome-desktop, which
  Tenko does not ship.
