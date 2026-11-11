# Freedesktop compliance

Tenko tracks its conformance with the [freedesktop.org specifications][specs]
and the companion standards the XFCE desktop relies on.  Every specification
has a version, a disposition, and either evidence or a linked work issue.
`tenko audit` parses the matrix below, so keep its table format.

[specs]: https://specifications.freedesktop.org/

## Scope

Tenko ships XFCE on X11.  Most protocol implementations come from XFCE, GTK,
GLib, gvfs and systemd; distro work is packaging, desktop-profile membership,
configuration, database triggers and verification.  Upstream implementation
bugs are reported upstream.

Repackaged vendor bundles under `/opt` are audited, but upstream metadata
defects inside those bundles do not block the distro's own compliance; they
are listed as allowed upstream findings in the audit.

Wayland-only and draft specifications are N/A for this release.

## Dispositions

| value | meaning | audit treatment |
|---|---|---|
| **implemented** | the component ships and the protocol is in use | any failing check fails the audit |
| **partial** | the component exists but the distro integration is incomplete | failures are reported as `OPEN` and owned by the linked issue |
| **gap** | no usable implementation ships | failures are reported as `OPEN` and owned by the linked issue |
| **N/A** | not applicable to an X11/XFCE distro, or application-owned | no check is run; the rationale must be recorded |

A `partial` or `gap` row must link at least one issue.  When the last issue for
a row closes, change the disposition to `implemented`; the audit then treats
any remaining failure as fatal.  This keeps the harness green while work is
open without weakening the end state.

## Audit policy

- `desktop-file-validate` must report no errors.  Warnings and hints are
  allowed because most of them are upstream translation text or deprecated
  keys that the distro does not own; the audit prints a warning count.
- `appstreamcli validate --no-net` must report no errors.  Warnings and
  informational messages are allowed.  A vendor bundle may be listed in
  `UPSTREAM_APPSTREAM_ERRORS` in `scripts/check/fdo_audit.py` with an issue
  number; the Chrome bundle is the only entry (#42).
- Icon themes must inherit only themes that are installed, and every `Icon=`
  in an application or autostart entry must resolve in hicolor, an installed
  theme, or `/usr/share/pixmaps`.
- Cache updates must be file triggers, not ad-hoc `%post` calls:
  `update-desktop-database` for `/usr/share/applications`,
  `update-mime-database` for `/usr/share/mime`, and
  `gtk-update-icon-cache` for `/usr/share/icons`.
- The audit is network-free.  Run it against the built repository with
  `tenko audit --rpm-dir build/repo-publish/6`; see
  [`testing.md`](testing.md).

## Matrix

| Spec | Version | Disposition | Evidence / work |
|---|---|---|---|
| `appstream` | current docs | implemented | appstreamcli in the desktop profiles; distro OS metainfo; validation in the audit |
| `autostart` | 0.5 | implemented | xfce4-session reads /etc/xdg/autostart |
| `basedir` | 0.8 | implemented | XDG base directories honoured; ~/.local/bin in PATH for login and interactive shells; runtime check in `tenko qemu fdo` |
| `clipboard` | 1.0 | N/A | Wayland data-device protocol; X11 uses X selections |
| `clipboard-extensions` | 1.0 | N/A | Wayland-only |
| `dbus` | current spec | implemented | dbus-daemon/dbus-x11 in base and desktop; policy files parsed by the audit |
| `desktop-entry` | 1.5 | implemented | Entries validate with no errors; update-desktop-database file trigger; checked by the audit |
| `fhs` | 3.0 | implemented | Merged-/usr layout plus /media, /var/local and the /usr/local subdirectories; /var/run and /var/lock via systemd tmpfiles |
| `global-shortcuts` | draft | N/A | Portal/Wayland; no Wayland session |
| `help-system` | current spec | implemented | /usr/share/help layout plus the tenko-help handler; documented browser fallback |
| `icon-naming` | 0.8.90 | implemented | Kora and Adwaita inherit hicolor; every application Icon= resolves |
| `icon-theme` | 0.13 | implemented | Themes inherit only installed themes; gtk-update-icon-cache file trigger |
| `idle-inhibit` | 0.1 | N/A | Wayland protocol; X11 uses XScreenSaver |
| `intent-apps` | 1.0.0 | N/A | New spec with no XFCE-stack implementation; revisit later |
| `menu` | 1.1 | implemented | garcon xfce-applications.menu and xfce-settings-manager.menu validate |
| `mime-apps` | 1.0.1 | implemented | /etc/xdg/mimeapps.list defaults; xdg-utils and desktop-file-utils in the desktop profiles |
| `mpris` | current spec | N/A | Application responsibility (media players); no distro service |
| `notification` | 1.3 | implemented | xfce4-notifyd 0.9.7 in the desktop profiles; dunst remains the non-XFCE alternative |
| `polkit` | current docs | implemented | polkitd, xfce-polkit agent and the wheel admin rule; policy files parsed by the audit |
| `recent-files` | 0.3 | implemented | gvfsd-recent via gvfs (required by Thunar); recent:// checked in `tenko qemu fdo` |
| `secret-service` | 0.2 | implemented | gnome-keyring 50.0 Secret Service, PAM login unlock and portal Secret backend |
| `shortcuts` | draft | N/A | Portal/Wayland; no Wayland session |
| `shared-mime-info` | 0.22 | implemented | MIME database packaged; update-mime-database file trigger |
| `sound-naming` | 0.2 | implemented | freedesktop stereo event sounds; XSettings default in tenko-desktop-config |
| `sound-theme` | 0.2 | implemented | sound-theme-freedesktop 0.8 with a valid index.theme; desktop profiles require it |
| `startup-notification` | 0.2 | implemented | Library and xfwm4 support packaged; checked in the session check |
| `status-notifier-item` | 0.1 draft | N/A | Draft; no maintained XFCE SNI host is packaged (see the tray section) |
| `systemtray` | 0.3 | implemented | xfce4-panel systray plugin in the default panel; _NET_SYSTEM_TRAY_S0 checked in the session check |
| `terminal-intent` | draft | N/A | Draft/Wayland-oriented; no implementation |
| `thumbnail` | 0.8.0/0.9.0 | implemented | tumbler covers, desktop files, fonts, JPEG and pixbuf; video/audio unsupported and documented below |
| `trash` | 1.0 | implemented | gvfsd-trash via gvfs; home layout tested; cross-filesystem limitation documented below |
| `wm` | 1.5 | implemented | xfwm4; EWMH atoms checked in the session check |
| `xembed` | 0.5 | implemented | xfce4-panel systray plugin (XEmbed host); checked in the session check |
| `xsettings` | 0.5 | implemented | xfsettingsd; checked in the session check |
| `XDG user dirs` | current spec | implemented | xdg-user-dirs 0.20 in the desktop profiles; the autostart entry creates ~/.config/user-dirs.dirs and the standard directories |
| `xdg-desktop-portal` | 1.22 | implemented | portal, GTK backend and Flatpak in the desktop profiles; xfce-portals.conf defaults to gtk; xfce-session.target starts graphical-session.target, checked in a real LightDM login by `tenko qemu fdo`; unsupported interfaces documented |

## XDG base directory exceptions

The XDG Base Directory specification covers application data, configuration,
cache and state.  Applications keep to those directories except in the cases
below; each is deliberate or owned by an upstream application.

| Path | Owner | Rationale |
|---|---|---|
| `~/.pyenv` | pyenv | Upstream's default root for interpreters and shims; users may set `PYENV_ROOT`, and `/etc/profile.d/pyenv.sh` only initialises when the directory already exists |
| `~/.ssh`, `~/.gnupg` | OpenSSH, GnuPG | Security-sensitive upstream layouts that predate XDG and must not be redirected |
| `~/.Xauthority`, `~/.ICEauthority` | X11 / XFCE session | X11 cookie files consumed before the session environment exists |
| `~/.bashrc`, `~/.bash_profile` | shell convention | Shell startup files are not application state |

XFCE itself uses `~/.config`, `~/.cache` and `~/.local/share` as required by
the specification.

## Help System fallback

Tenko does not ship a dedicated help browser.  Documents are installed under
`/usr/share/help/<id>/index.html` (and the `C` locale fallback), and
`tenko-help` resolves `help:<id>` in this order: the user's locale, the
language, `C`, the id without a locale, then the generic Tenko page.  It
opens the page through `xdg-open`; if no HTML handler is configured it prints
the resolved path instead.  `/etc/xdg/mimeapps.list` maps
`x-scheme-handler/help` to `tenko-help.desktop`, so `xdg-open help:tenko`
works on a full desktop (through the XFCE preferred browser) and degrades to
the printed path on a minimal install.

## Trash and recent files

gvfs supplies `gvfsd-trash`, `gvfsd-recent` and `gvfsd-metadata`; Thunar
requires gvfs, so `trash://` and `recent://` are available on a desktop
install.  The home trash layout is `$XDG_DATA_HOME/Trash/{files,info}` with
`Path` and `DeletionDate` in each `.trashinfo`, as required by Trash 1.0.

GLib's local trash refuses to move a file across filesystem boundaries on
some system-internal mounts (it reports "system internal mounts" or "across
filesystem boundaries" instead of creating a top-directory trash).  This is
an upstream GLib limitation, not a distro configuration choice.  Files on
the same filesystem as the home trash, including the common `/home` case,
are handled; this cross-filesystem behaviour is not a data-loss bug.

## Thumbnail support

tumbler ships the cover, desktop, font, JPEG and pixbuf thumbnailers.  The
GStreamer thumbnailer is deliberately disabled: Tenko does not package the
codec set it would need for reliable video and audio thumbnails, and
`libffmpegthumbnailer` is not packaged either.  Image, font, cover and
desktop-file thumbnails are supported; video and audio thumbnails are
**unsupported** and fall back to the application's generic icon.  Adding a
codec-backed thumbnailer later means packaging the required plugins and
re-enabling the plugin in the tumbler spec together with the file list.

## Polkit and D-Bus

`polkitd` runs on the system bus and ships `pkexec`, `pkcheck`, `pkaction`
and `pkttyagent`.  The session starts `xfce-polkit` from
`/etc/xdg/autostart/xfce-polkit.desktop`; its `NotShowIn=GNOME;KDE;` line
keeps it out of other desktops.  The installer creates the admin account in
`wheel` and locks root, so `/etc/polkit-1/rules.d/50-tenko-wheel.rules`
makes `unix-group:wheel` the polkit administrator; accountsservice's
existing `adm` rule is left in place for compatibility.  Actions and rules
ship with the packages that own them (NetworkManager, accountsservice,
flatpak, polkit itself).

The audit parses every `/usr/share/dbus-1` and `/etc/dbus-1` configuration
file and the polkit `.policy` XML.  The runtime prompt is exercised by the
`tenko qemu fdo` gate; the system bus must start without policy parse
errors.

## AppStream

`appstream` 1.2.2 is part of the desktop profiles, so `appstreamcli` and the
metadata readers are installed.  Distro metadata is
`/usr/share/metainfo/org.tenko.Tenko.metainfo.xml` (type
`operating-system`, id `org.tenko.Tenko`) from `tenko-release`; application
metadata ships with the applications themselves (Thunar, xfce4-appfinder,
xfce4-power-manager, nm-connection-editor, AppStream's own CLI and the
Chrome bundle).

Every metainfo file is validated with `appstreamcli validate --no-net` by the
audit.  The Chrome bundle's `type-property-required` error is an upstream
vendor defect and is waived in the "Allowed upstream findings" table below;
it does not block distro metadata.  Tenko does not ship a pre-composed
catalogue: `appstreamcli search` reads the installed metainfo at runtime,
and a repository-wide catalogue can be generated from an installed root with
`appstreamcli compose` when a software centre needs one.  That is a
deliberate decision, not an omission.

## Sound theme

`sound-theme-freedesktop` 0.8 installs the freedesktop theme under
`/usr/share/sounds/freedesktop` with `Directories=stereo` and the standard
event names.  `tenko-desktop-config` sets the XSettings `SoundThemeName` to
`freedesktop`, and the desktop profiles require the package.  libcanberra's
own default and fallback theme is `freedesktop`, so a missing configured
theme still resolves instead of failing silently.  The runtime check uses
`canberra-gtk-play -i bell` and `-i dialog-error`.

## Desktop notifications

`xfce4-notifyd` 0.9.7 is the default notification daemon; its D-Bus
activation file names `org.freedesktop.Notifications` and the
`/etc/xdg/autostart/xfce4-notifyd.desktop` entry (`OnlyShowIn=XFCE;`) starts
it with the session.  It advertises `body`, `body-markup`, `actions` and
`icon-static`, stores notification history in SQLite, and implements the
standard `Notify`, `CloseNotification`, `GetCapabilities`,
`GetServerInformation` and `GetNotifications` calls.  Upstream does not
return the literal `persistence` capability string even though it keeps a
history; this is an upstream implementation detail rather than a missing
distro component.

`dunst` 1.13.2 remains packaged as the non-XFCE alternative and is not part
of the desktop profile.  The QEMU check runs `notify-send`, a
notification with an action, and introspects the service owner.

## Secret Service

`gnome-keyring` 50.0 is the Secret Service provider.  It owns
`org.freedesktop.secrets`, ships the login keyring, the PKCS#11 module, the
gcr prompter integration and the `pam_gnome_keyring` module.  LightDM's PAM
configuration adds the optional auth and session hooks, so a password typed
at the greeter unlocks the login keyring; autologin starts the daemon
without an unlock and prompts later if a secret is requested.  The provider
is part of both desktop profiles.

gnome-keyring also ships `gnome-keyring.portal`, so
`/etc/xdg/mimeapps.list`-independent portal configuration selects
`org.freedesktop.impl.portal.Secret=gnome-keyring` and sandboxed
applications reach the same keyring through the portal.  `libsecret`'s
`secret-tool` is the command-line check used by the QEMU test
(store/lookup round-trip, collections, aliases and locked-keyring prompt).

## Portals and Flatpak

Tenko ships `xdg-desktop-portal` 1.22.1, the `xdg-desktop-portal-gtk` 1.15.3
backend, `xdg-dbus-proxy`, `bubblewrap` and `flatpak` 1.18.4 in the default
desktop profiles.  Flatpak is part of the default install; the Flathub remote
is shipped through `/usr/share/flatpak/remotes.d/flathub.flatpakrepo`, and
`/etc/polkit-1/rules.d/50-tenko-flatpak.rules` lets active local `wheel`
users manage system remotes and install local bundles.

`xfce-portals.conf` selects `default=gtk` instead of naming xapp (not
packaged) and the Wayland-only wlr ScreenCast backend.  The GTK backend
implements FileChooser, AppChooser, Print, Notification, Inhibit, Access,
Account, Email, DynamicLauncher, Lockdown and Settings.  Screenshot,
ScreenCast, Background and Wallpaper have no backend in this release:
Screenshot/Background/Wallpaper would need xapp, and ScreenCast is
Wayland-oriented.  The Secret interface uses the gnome-keyring backend from
the Secret Service section above.  Applications using the unsupported
interfaces get the portal's normal "not supported" reply rather than a
broken activation.

The QEMU check introspects `org.freedesktop.portal.Desktop`, opens a
file chooser and OpenURI, sends a notification and confirms the document
portal and permission store activate.  It runs from a LightDM autologin
session with a systemd user manager, waits for `graphical-session.target` and
`xfce-session.target`, and requires `xdg-desktop-portal.service` to be
activated by the user manager; a private dbus-launch bus is a harness
failure, not a portal pass.

XFCE 4.20 does not start its session through systemd, so nothing activates
`graphical-session.target`; `xdg-desktop-portal.service` uses
`Requisite=graphical-session.target` and therefore cannot be D-Bus activated
in a plain XFCE session.  `tenko-desktop-config` ships `xfce-session.target`
(`BindsTo=graphical-session.target`) together with an `/etc/xdg/autostart`
entry that exports `DISPLAY`/`XAUTHORITY` to the user manager and starts the
target.  `xfce-session-watch.service` stops the target when `xfce4-session`
exits, so the next login starts a fresh session instead of reusing the
previous portal and environment.

## System tray and StatusNotifierItem

The default XFCE panel includes the `systray` plugin (`libsystray.so`), which
implements the XEmbed System Tray 0.3 protocol.  The session checker verifies
that an owner holds `_NET_SYSTEM_TRAY_S0` and that the panel configuration
contains the plugin.  XEmbed clients such as `nm-applet` therefore appear and
activate normally.

StatusNotifierItem is a draft specification and Tenko does not ship an SNI
host: the available XFCE SNI plugins are unmaintained and would add a second
tray implementation to the panel.  Applications that *only* provide an SNI
icon (some modern Electron/Flatpak apps) may not show a tray icon; this is
the documented limitation.  Revisit if a maintained host is packaged and the
default panel can carry both.

## Runtime verification

The static audit checks that components are packaged and configured.  The
protocol rows that need a running session (autostart, startup notification,
XSettings, EWMH, notifications, trash/recent, polkit, portals, sound, tray)
are checked by `tenko qemu fdo` in a real login session; see
[`testing.md`](testing.md).

## Allowed upstream findings

These findings belong to upstream or vendor bundles and do not block the
distro's own compliance.  Revisit an entry when the bundle or upstream
metadata changes.

| Finding | Issue | Rationale |
|---|---|---|
| `google-chrome.appdata.xml`: `type-property-required` | #42 | Google Chrome vendor bundle metadata; fixed by the bundle or replaced by distro metadata |
| XFCE helper `.desktop` files under `/usr/share/xfce4/helpers` | — | XFCE private helper format, not Desktop Entry; not validated as application entries |
| GTK module `.desktop` files under `/usr/lib64/gnome-settings-daemon-3.0` | — | GTK module descriptor format, not Desktop Entry |
| Xsession `.desktop` files under `/usr/share/xsessions` | — | Xsession format, not an application entry; verified in the session checks |
