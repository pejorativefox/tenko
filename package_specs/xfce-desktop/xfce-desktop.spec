Name:       xfce-desktop
Version:    4.20
Release:    12
Summary:    Tenko XFCE 4.20 desktop meta-package
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
Requires:   mpv
Requires:   xfdesktop
Requires:   xfce4-power-manager
Requires:   dbus-daemon
Requires:   dbus-x11
Requires:   xorg-server
Requires:   lightdm
Requires:   accountsservice
Requires:   sudo
Requires:   librsvg
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
# shared-mime-info used to be pulled in by gdk-pixbuf's .pc Requires.
# The .pc ships in the gdk-pixbuf runtime package again after the -devel
# subpackages were removed, but Thunar/GIO need the MIME database at
# runtime, so require the data package explicitly.
Requires:   shared-mime-info
Requires:   tenko-desktop-config
Requires:   linux-firmware-base
# udev's hardware database is what maps PCI/USB/input IDs to device
# properties.  It is a Recommends of systemd so containers can omit it, but
# a desktop install runs on real hardware and must have it even when the
# install is done with install_weak_deps=False.
Requires:   systemd-hwdb
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
The Tenko XFCE 4.20 desktop: X11 only, no Wayland.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/share/tenko
touch %{buildroot}/usr/share/tenko/xfce-desktop

%files
/usr/share/tenko/xfce-desktop

%post
# The base system boots to multi-user.target.  A desktop profile should come
# up in the graphical target so lightdm (required above) starts the greeter.
if [ -x /usr/bin/systemctl ]; then
    systemctl set-default graphical.target >/dev/null 2>&1 || :
fi

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 4.20-12
- Require mpv so the default desktop install ships the mpv video player.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 4.20-11
- Drop the browneye marker cleanup; no Browneye installs remain.

* Fri Nov 06 2026 tenko <build@tenko.invalid> 4.20-10
- Use tenko-desktop-config and the /usr/share/tenko marker; clean up the
  old browneye marker on upgrade.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20-9
- Require librsvg for SVG icon/wallpaper rendering

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20-8
- Require sudo so the installer's administrative wheel user can escalate

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20-7
- Require accountsservice so the LightDM greeter lists local users and
  their icons instead of only offering "Other..."

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20-6
- Require lightdm: the desktop profile now provides a graphical login
- Set the default systemd target to graphical.target in %post so the
  greeter starts on boot (the base defaults to multi-user.target)

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20-5
- Require shared-mime-info explicitly: gdk-pixbuf used to pull it in
  through its .pc Requires, which now lives in gdk-pixbuf-devel, but the
  MIME database is runtime data needed by Thunar/GIO
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20-4
- Require systemd-hwdb: it is only a Recommends of systemd, and image
  builds use install_weak_deps=False, so without a hard requirement a
  desktop install on real hardware would lose the udev hardware database
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
