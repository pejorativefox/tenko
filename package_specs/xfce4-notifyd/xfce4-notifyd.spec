Name:       xfce4-notifyd
Version:    0.9.7
Release:    1
Summary:    Notification daemon for the Xfce desktop
License:    GPL-2.0-only AND GPL-2.0-or-later
URL:        https://docs.xfce.org/apps/notifyd/start
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: harfbuzz
BuildRequires: libnotify
BuildRequires: libx11
BuildRequires: libxfce4ui
BuildRequires: libxfce4util
BuildRequires: pango
BuildRequires: xfce4-panel
BuildRequires: xfconf
BuildRequires: dbus-daemon
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: fribidi
BuildRequires: libXdmcp
BuildRequires: libdrm
BuildRequires: libepoxy
BuildRequires: libjpeg-turbo
BuildRequires: liblzo2
BuildRequires: libpciaccess
BuildRequires: libpng
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
BuildRequires: pixman
BuildRequires: shared-mime-info
BuildRequires: xorgproto

%description
xfce4-notifyd is a notification daemon for the Xfce desktop.  It implements
the server side of the freedesktop.org Desktop Notifications specification
(org.freedesktop.Notifications).

%package lang
Summary:    xfce4-notifyd translations
Requires:   xfce4-notifyd = %{version}-%{release}

%description lang
Translations for xfce4-notifyd.

%prep
%setup

%build
%configure \
    --disable-wayland \
    --disable-sound \
    --disable-systemd
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfce4-notifyd.filelist
%files lang -f %{_sourcedir}/xfce4-notifyd-lang.filelist


%changelog
* Sun Nov 08 2026 browneye <build@browneye.invalid> 0.9.7-1
- Initial package, latest stable upstream release 0.9.7.
- Verify the SPDX licence expression from COPYING and the source headers:
  GPL-2.0-only for the daemon and configuration UI, GPL-2.0-or-later for
  the panel plugin (issue #8).
- Build X11-only (--disable-wayland) and without libcanberra sound support
  (--disable-sound): gdk-wayland, gtk-layer-shell and libcanberra-gtk3 are
  not in the build image.  Notifications still support body, markup,
  actions, icons and the SQLite notification log.
- Disable the systemd user unit (--disable-systemd) so the XDG autostart
  entry starts the daemon directly; D-Bus activation remains the primary
  startup path, as for dunst.
