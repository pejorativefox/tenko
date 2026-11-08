Name:       xfce-desktop-core
Version:    4.20
Release:    8
Summary:    Tenko XFCE 4.20 core desktop (VM/headless, no vendor firmware)
License:    MIT
Prefix:     /usr

# Self-contained runtime desktop: runtime base, kernel, X11 server and the
# XFCE session.  No GPU firmware/vendor packs and no hwdb, so this is the
# profile for QEMU/VMs and headless boxes.
Requires:   tenko-base-runtime
Requires:   linux-kernel
# Networking UI, same as the full desktop profile: NetworkManager's preset
# enables the service on boot and the applet's /etc/xdg/autostart entry is
# launched by xfce4-session.
Requires:   NetworkManager
Requires:   network-manager-applet
# Flatpak support, same as the full desktop profile: flatpak present at
# session start, a polkit authentication agent, and the portal backend
# (issue #29).
Requires:   flatpak
Requires:   xfce-polkit
Requires:   xdg-desktop-portal
Requires:   xdg-desktop-portal-gtk
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
# The new-user XFCE defaults from tenko-desktop-config name Arc-Dark,
# Kora and Terminus; the XFCE packages do not pull those in.
Requires:   arc-theme
Requires:   kora-icon-theme
Requires:   font-terminus
Requires:   shared-mime-info
# Creates ~/.config/user-dirs.dirs and the localized Desktop, Documents,
# Downloads, Music, Pictures and Videos directories at session start.
Requires:   xdg-user-dirs
# Desktop entry, MIME and icon metadata: xdg-utils provides the xdg-*
# tools, desktop-file-utils validates/updates the entry database (and now
# owns the file trigger), and mpv is the default media handler in
# /etc/xdg/mimeapps.list.
Requires:   xdg-utils
Requires:   desktop-file-utils
Requires:   mpv
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
Requires:   tenko-desktop-config

%description
A lean, self-contained XFCE 4.20 desktop for virtual machines and
headless/embedded systems: tenko-base-runtime plus the kernel, X11
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
mkdir -p %{buildroot}/usr/share/tenko
touch %{buildroot}/usr/share/tenko/xfce-desktop-core

%files
/usr/share/tenko/xfce-desktop-core

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-8
- Require xdg-utils, desktop-file-utils and mpv so the core profile has the
  desktop metadata tools, the entry database trigger and the default media
  handler named by /etc/xdg/mimeapps.list (issue #35).
- Require flatpak, xfce-polkit, xdg-desktop-portal and
  xdg-desktop-portal-gtk, matching the xfce-desktop profile: flatpak is
  present at session start, auth_admin prompts work and flatpak apps get
  the GTK portal backend (issue #29).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-7
- Require xdg-user-dirs so a new account gets ~/.config/user-dirs.dirs and
  the standard localized user directories at session start (issue #34).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-6
- Require NetworkManager and network-manager-applet so the core session
  has the network manager running on boot and the panel applet, matching
  the xfce-desktop profile.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 4.20-5
- Require arc-theme, kora-icon-theme and font-terminus so the default
  new-user XFCE look from tenko-desktop-config resolves.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 4.20-4
- Drop the browneye marker cleanup; no Browneye installs remain.

* Fri Nov 06 2026 tenko <build@tenko.invalid> 4.20-3
- Use tenko-base-runtime/tenko-desktop-config and the /usr/share/tenko
  marker; clean up the old browneye marker on upgrade.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20-2
- Require shared-mime-info: the MIME database used to arrive through
  gdk-pixbuf's .pc Requires and is runtime data, not a build dependency
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20-1
- New XFCE core profile: runtime base, kernel, X11 server, fonts, D-Bus
  and the XFCE session without vendor firmware, hwdb or Mesa (plan D25)
