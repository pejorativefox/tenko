Name:       xfce-desktop-core
Version:    4.20
Release:    19
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
# Game controller and Steam hardware permissions, matching the full desktop
# profile.  The Steam Flatpak checks /dev/uinput before it warns that
# steam-devices is missing.
Requires:   steam-devices
# AppImage type-2 runtimes are built against FUSE 2 and dlopen
# libfuse.so.2 at startup; fuse3 ships a different soname and cannot
# satisfy them.
Requires:   fuse2
# Secret Service provider (org.freedesktop.secrets) and portal Secret
# backend.
Requires:   gnome-keyring
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
# Color emoji for GUI applications and the desktop terminal; the base system
# ships the monochrome Noto Emoji face for kmscon.
Requires:   font-noto-color-emoji
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
# Software metadata: appstreamcli and the installed metainfo.
Requires:   appstream
# Creates ~/.config/user-dirs.dirs and the localized Desktop, Documents,
# Downloads, Music, Pictures and Videos directories at session start.
Requires:   xdg-user-dirs
# Event sounds through libcanberra (Sound Theme 0.2 / Sound Naming 0.2).
Requires:   sound-theme-freedesktop
# Playback for the sound theme and the libsecret client tools.
Requires:   libcanberra
Requires:   libsecret
# Desktop entry, MIME and icon metadata: xdg-utils provides the xdg-*
# tools, desktop-file-utils validates/updates the entry database (and now
# owns the file trigger), mpv handles audio/video and ristretto is the
# default image viewer in /etc/xdg/mimeapps.list.
Requires:   xdg-utils
Requires:   desktop-file-utils
Requires:   mpv
Requires:   ristretto
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
# XFCE-native Desktop Notifications 1.3 daemon.
Requires:   xfce4-notifyd
Requires:   xfce4-appfinder
Requires:   xfce4-terminal
# Command-line X selection access for scripts and terminal users.
Requires:   xsel
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
* Tue Nov 10 2026 tenko <build@tenko.invalid> 4.20-19
- Require xsel so the lean VM/headless desktop profile also has
  command-line access to the X selections.

* Tue Nov 10 2026 tenko <build@tenko.invalid> 4.20-18
- Require ristretto so the image defaults in /etc/xdg/mimeapps.list
  resolve on the core profile as well.  mpv stays for audio and video.

* Tue Nov 10 2026 tenko <build@tenko.invalid> 4.20-17
- Require steam-devices so the core profile also ships Valve's controller
  udev rules.  Without them /dev/uinput is root-only and the Steam Flatpak
  warns that the steam-devices package is missing.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-16
- Require font-noto-color-emoji for color emoji in GUI applications and the
  desktop terminal.  The base system keeps the monochrome Noto Emoji face
  that kmscon can render.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-15
- Require fuse2 so AppImage type-2 executables can mount their squashfs
  image through libfuse.so.2.  fuse3 alone is not enough: the type-2
  runtime loads libfuse.so.2 and a different soname cannot satisfy it.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-14
- Require libcanberra and libsecret so the sound theme has a player and
  libsecret applications have the client tools on a default desktop
  (issues #39, #43).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-13
- Require gnome-keyring as the Secret Service provider and portal Secret
  backend (issue #39).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-12
- Require appstream so appstreamcli is present and the installed metainfo
  can be validated and searched on a desktop install (issue #42).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-11
- Require xfce4-notifyd 0.9.7 so org.freedesktop.Notifications has an
  owner on a default desktop (issue #37).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-10
- Require sound-theme-freedesktop so libcanberra event sounds resolve
  (issue #43).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-9
- Require xfce-polkit so the core session has a polkit authentication
  agent for auth_admin actions (issue #40).

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
