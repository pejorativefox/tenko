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
BuildRequires: shared-mime-info
BuildRequires: xorgproto
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: dbus-daemon
BuildRequires: freetype
BuildRequires: fribidi
BuildRequires: harfbuzz
BuildRequires: libXdmcp
BuildRequires: libdrm
BuildRequires: libepoxy
BuildRequires: libjpeg-turbo
BuildRequires: liblzo2
BuildRequires: libpciaccess
BuildRequires: libpng
BuildRequires: libx11
BuildRequires: libxau
BuildRequires: libxcb
BuildRequires: libxcomposite
BuildRequires: libxcursor
BuildRequires: libxdamage
BuildRequires: libxext
BuildRequires: libxfixes
BuildRequires: libxft
BuildRequires: libxi
BuildRequires: libxinerama
BuildRequires: libxrandr
BuildRequires: libxrender
BuildRequires: libxres
BuildRequires: libxtst
BuildRequires: libxxf86vm
BuildRequires: mesa
BuildRequires: pango
BuildRequires: pixman

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
