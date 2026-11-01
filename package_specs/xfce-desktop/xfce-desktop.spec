Name:       xfce-desktop
Version:    4.20
Release:    4
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
Requires:   xfce4-terminal
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
Requires:   xwininfo
Requires:   xwd
Requires:   hicolor-icon-theme
Requires:   browneye-desktop-config
Requires:   linux-firmware-base
# Weak dependencies: a normal install still gets every vendor pack, while
# --setopt=install_weak_deps=False (image builds, VMs) installs only base.
Recommends: linux-firmware-intel-wifi
Recommends: linux-firmware-nvidia
Recommends: linux-firmware-amd-gpu
Recommends: linux-firmware-intel-gpu
Recommends: linux-firmware-mediatek
Recommends: linux-firmware-ath
Recommends: linux-firmware-bluetooth
Recommends: linux-firmware-nic
Recommends: linux-firmware-other

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
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20-4
- Require only linux-firmware-base and Recommend the vendor firmware packs
  (size audit firmware split).  With install_weak_deps=False an image now
  gets the regulatory database without the 395 MB vendor set, while a
  normal install still pulls every pack.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20-3
- Require xfce4-terminal so the desktop install includes a terminal

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20-2
- Require linux-firmware for the desktop/hardware install

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20-1
- Initial XFCE 4.20 desktop meta-package
