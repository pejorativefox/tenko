Name:       xfce-desktop-core
Version:    4.20
Release:    2
Summary:    Browneye XFCE 4.20 core desktop (VM/headless, no vendor firmware)
License:    MIT
Prefix:     /usr

# Self-contained runtime desktop: runtime base, kernel, X11 server and the
# XFCE session.  No GPU firmware/vendor packs and no hwdb, so this is the
# profile for QEMU/VMs and headless boxes.
Requires:   browneye-base-runtime
Requires:   linux-kernel
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
Requires:   shared-mime-info
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
Requires:   xfce4-appfinder
Requires:   xfce4-terminal
Requires:   xfdesktop
Requires:   browneye-desktop-config

%description
A lean, self-contained XFCE 4.20 desktop for virtual machines and
headless/embedded systems: browneye-base-runtime plus the kernel, X11
server (modesetting/vesa), input driver, fonts, D-Bus and the XFCE
session.

No vendor firmware, no udev hwdb database, no Mesa userspace and no
GPU drivers: a VM using virtio/vesa or a server with a serial/remote
console needs none of them.  Install xfce-desktop for the same session
with the firmware base and weak vendor-pack recommendations, or
xfce-desktop-full for the complete hardware desktop.

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/browneye
touch %{buildroot}/usr/share/browneye/xfce-desktop-core

%files
/usr/share/browneye/xfce-desktop-core

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20-2
- Require shared-mime-info: the MIME database used to arrive through
  gdk-pixbuf's .pc Requires and is runtime data, not a build dependency
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20-1
- New XFCE core profile: runtime base, kernel, X11 server, fonts, D-Bus
  and the XFCE session without vendor firmware, hwdb or Mesa (plan D25)
