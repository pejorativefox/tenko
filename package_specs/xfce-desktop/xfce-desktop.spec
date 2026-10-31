Name:       xfce-desktop
Version:    4.20
Release:    1
Summary:    Browneye XFCE 4.20 desktop meta-package
License:    MIT
Prefix:     /usr

Requires:   libxfce4util
Requires:   xfconf
Requires:   libxfce4ui
Requires:   exo
Requires:   garcon
Requires:   libxfce4windowing
Requires:   xfce4-panel
Requires:   xfwm4
Requires:   xfce4-session
Requires:   xfce4-settings
Requires:   thunar
Requires:   thunar-volman
Requires:   tumbler
Requires:   xfce4-appfinder
Requires:   xfdesktop
Requires:   xfce4-power-manager
Requires:   dbus-daemon
Requires:   dbus-x11
Requires:   xorg-server
Requires:   xinit
Requires:   xauth
Requires:   xkeyboard-config
Requires:   xf86-input-libinput
Requires:   xf86-video-vesa
Requires:   iceauth
Requires:   font-alias
Requires:   font-bh-ttf
Requires:   xrdb
Requires:   xset
Requires:   xmodmap
Requires:   xhost
Requires:   hicolor-icon-theme
Requires:   browneye-desktop-config

%description
The Browneye XFCE 4.20 desktop: X11 only, no Wayland.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/share/browneye
touch %{buildroot}/usr/share/browneye/xfce-desktop

%files
/usr/share/browneye/xfce-desktop

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20-1
- Initial XFCE 4.20 desktop meta-package
