Name:       xfce-desktop
Version:    4.20
Release:    29
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
# XFCE-native Desktop Notifications 1.3 daemon.  dunst stays in the
# repository as the non-XFCE alternative but is not part of this profile.
Requires:   xfce4-notifyd
Requires:   xfce4-appfinder
Requires:   xfce4-terminal
# Image viewing and manipulation: Ristretto is the default image viewer
# (registered for image MIME types by its desktop file), ImageMagick ships
# the command-line convert/magick tools and format delegates.
Requires:   ristretto
Requires:   imagemagick
Requires:   mpv
# Default web browser: the Google Chrome vendor bundle under /opt, with its
# /usr/bin entry points and desktop file as required for repackaged bundles.
# Its upstream appstream defect is waived in the freedesktop audit (#42).
Requires:   google-chrome-bin
Requires:   xfdesktop
Requires:   xfce4-power-manager
# Panel volume control and VA-API video acceleration.  The plugin pulls
# PulseAudio at runtime; libva is the API used by the video stack and its
# GLX backend brings in libGL.
Requires:   xfce4-pulseaudio-plugin
Requires:   libva
# Bluetooth: bluez ships the daemon, bluetoothctl and the systemd/D-Bus
# integration; pulseaudio-bluez adds the A2DP/HFP modules so paired audio
# devices become normal sinks the panel plugin can select.  Vendor Bluetooth
# firmware stays a weak recommendation here (hard requirement of
# xfce-desktop-hardware), matching the rest of the firmware split.
Requires:   bluez
Requires:   pulseaudio-bluez
Requires:   dbus-daemon
Requires:   dbus-x11
Requires:   xorg-server
Requires:   lightdm
Requires:   accountsservice
Requires:   sudo
# Networking UI.  NetworkManager is the manager the base install uses (its
# preset enables the service and turns systemd-networkd off); nm-applet puts
# connection status in the panel and ships the /etc/xdg/autostart entry that
# xfce4-session launches at login.
Requires:   NetworkManager
Requires:   network-manager-applet
# Flatpak support.  flatpak must be present when the session starts so the
# systemd user environment generator adds the flatpak exports directories to
# XDG_DATA_DIRS; xfce-polkit provides the polkit authentication agent the
# auth_admin actions need; the portal backend gives sandboxed apps their file
# chooser, print and OpenURI integration (issue #29).
Requires:   flatpak
Requires:   xfce-polkit
Requires:   xdg-desktop-portal
Requires:   xdg-desktop-portal-gtk
# AppImage type-2 runtimes are built against FUSE 2 and dlopen
# libfuse.so.2 at startup; fuse3 ships a different soname and cannot
# satisfy them.
Requires:   fuse2
# Secret Service provider (org.freedesktop.secrets) for libsecret apps and
# the portal Secret backend.
Requires:   gnome-keyring
Requires:   librsvg
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
# tenko-desktop-config ships new-user XFCE defaults that name Arc-Dark
# (GTK/Xfwm), Kora (icons) and Terminus (terminal font).  The XFCE packages
# do not pull those data packages in, so the desktop profile must.
Requires:   arc-theme
Requires:   kora-icon-theme
Requires:   font-terminus
# Event sounds through libcanberra (Sound Theme 0.2 / Sound Naming 0.2).
Requires:   sound-theme-freedesktop
# Playback for the sound theme (canberra-gtk-play) and the libsecret client
# tools used by desktop applications (secret-tool).
Requires:   libcanberra
Requires:   libsecret
# shared-mime-info used to be pulled in by gdk-pixbuf's .pc Requires.
# The .pc ships in the gdk-pixbuf runtime package again after the -devel
# subpackages were removed, but Thunar/GIO need the MIME database at
# runtime, so require the data package explicitly.
Requires:   shared-mime-info
# Software metadata: appstreamcli validates and searches the installed
# metainfo; the repository catalogue decision is documented in
# docs/freedesktop.md.
Requires:   appstream
# Creates ~/.config/user-dirs.dirs and the standard user directories at
# session start.
Requires:   xdg-user-dirs
Requires:   xdg-utils
Requires:   desktop-file-utils
Requires:   tenko-desktop-config
Requires:   linux-firmware-base
# udev's hardware database is what maps PCI/USB/input IDs to device
# properties.  It is a Recommends of systemd so containers can omit it, but
# a desktop install runs on real hardware and must have it even when the
# install is done with install_weak_deps=False.
Requires:   systemd-hwdb
# Game controller and Steam hardware permissions.  Without the udev rules the
# Steam Flatpak warns that /dev/uinput is not accessible, and controllers are
# unusable in Steam, SteamVR, Wine and other launchers.
Requires:   steam-devices
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
* Tue Nov 10 2026 tenko <build@tenko.invalid> 4.20-29
- Require ristretto, the Xfce image viewer, and imagemagick for image
  viewing and command-line image manipulation on a default desktop.

* Tue Nov 10 2026 tenko <build@tenko.invalid> 4.20-28
- Require steam-devices so a desktop install ships Valve's controller udev
  rules.  Without them /dev/uinput is root-only and the Steam Flatpak warns
  that the steam-devices package is missing.

* Tue Nov 10 2026 tenko <build@tenko.invalid> 4.20-27
- Require bluez and pulseaudio-bluez: the desktop now has the Bluetooth
  daemon, bluetoothctl, and the PulseAudio A2DP/HFP modules behind the
  panel's volume control.  Bluetooth firmware is still a weak
  recommendation of this meta and a hard requirement of
  xfce-desktop-hardware.

* Mon Nov 09 2026 browneye <build@browneye.invalid> 4.20-26
- Require google-chrome-bin so the default desktop install ships the
  Google Chrome vendor bundle (156.0.8078.79) as its web browser.  The
  bundle installs under /opt with the /usr/bin entry points and desktop
  file; its upstream appstream defect remains the documented waiver in
  the freedesktop audit.

* Mon Nov 09 2026 browneye <build@browneye.invalid> 4.20-25
- Require xfce4-pulseaudio-plugin so the panel has volume/mute control and
  device selection on a default desktop; PulseAudio arrives through the
  plugin's libpulse dependency.
- Require libva so the VA-API video stack is available on the desktop
  profile.  The base OS carries udisks2/libblockdev, fwupd, lsof, strace
  and nano, so they are not repeated here.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-24
- Require font-noto-color-emoji for color emoji in GUI applications and the
  desktop terminal.  The base system keeps the monochrome Noto Emoji face
  that kmscon can render.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-23
- Require fuse2 so AppImage type-2 executables can mount their squashfs
  image through libfuse.so.2.  fuse3 alone is not enough: the type-2
  runtime loads libfuse.so.2 and a different soname cannot satisfy it.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-22
- Require libcanberra and libsecret so the sound theme has a player and
  libsecret applications have the client tools on a default desktop
  (issues #39, #43).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-21
- Require gnome-keyring as the Secret Service provider and portal Secret
  backend (issue #39).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-20
- Require appstream so appstreamcli is present and the installed metainfo
  can be validated and searched on a desktop install (issue #42).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-19
- Require xfce4-notifyd 0.9.7 so org.freedesktop.Notifications has an
  owner on a default desktop (issue #37).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-18
- Require sound-theme-freedesktop so libcanberra event sounds resolve
  (issue #43).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-17
- Require xfce-polkit so privileged desktop actions can show the polkit
  authentication dialog (issue #40).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-16
- Require xdg-utils and desktop-file-utils so the full desktop has the
  xdg-* tools and the desktop entry database trigger (issue #35).
- Require flatpak, xfce-polkit, xdg-desktop-portal and
  xdg-desktop-portal-gtk.  flatpak is present at first login, so the
  session environment includes the flatpak exports dirs instead of warning
  until a restart; xfce-polkit answers auth_admin prompts; the portal
  backend gives flatpak apps file chooser and OpenURI support (issue #29).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-15
- Require xdg-user-dirs so a new account gets ~/.config/user-dirs.dirs and
  the standard localized user directories at session start (issue #34).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20-14
- Require NetworkManager and network-manager-applet: a desktop install now
  starts the network manager on boot (the NetworkManager preset enables the
  service) and ships the panel applet.  xfce4-session autostarts it from the
  /etc/xdg/autostart/nm-applet.desktop entry in the applet package.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 4.20-13
- Require arc-theme, kora-icon-theme and font-terminus so the default
  new-user XFCE look from tenko-desktop-config resolves.

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
