Name:       tenko-desktop-config
Version:    6
Release:    8
Epoch:      1
Summary:    Tenko X11/XFCE session configuration
License:    MIT
URL:        https://pjfox.xyz/git/daspork/tenko
Prefix:     /usr

Requires:   xinit
Requires:   xfce4-session
Requires:   xdg-utils
Requires:   systemd
Requires:   procps-ng

%description
Default X session configuration for Tenko: startxfce4 on startx, plus the
default XFCE look (GTK/icon/Xfwm themes, the terminal profile and a single
top panel) for new users.  The desktop metas pull in the themes and font
these defaults name.

%prep

%build

%install
rm -rf %{buildroot}
xfconfdir=%{buildroot}/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml
mkdir -p %{buildroot}/etc/skel %{buildroot}/var/lib/xkb "$xfconfdir"
cat > %{buildroot}/etc/skel/.xinitrc <<'EOF'
#!/bin/sh
exec startxfce4
EOF
chmod 644 %{buildroot}/etc/skel/.xinitrc

# Desktop-level metadata shared by the XFCE profiles: default MIME
# associations, a help: URI handler and the Help System layout.
install -Dpm755 %{_sourcedir}/tenko-help %{buildroot}%{_bindir}/tenko-help
install -Dpm644 %{_sourcedir}/tenko-help.desktop \
    %{buildroot}%{_datadir}/applications/tenko-help.desktop
install -Dpm644 %{_sourcedir}/tenko-help.html \
    %{buildroot}%{_datadir}/help/tenko/index.html
install -Dpm644 %{_sourcedir}/tenko-help.html \
    %{buildroot}%{_datadir}/help/C/tenko/index.html
install -Dpm644 %{_sourcedir}/mimeapps.list \
    %{buildroot}%{_sysconfdir}/xdg/mimeapps.list

# XFCE does not start its session through systemd, so nothing pulls in
# graphical-session.target.  xdg-desktop-portal.service has
# Requisite=graphical-session.target and therefore refuses D-Bus activation
# in an XFCE session.  Ship a concrete session target, an autostart entry that
# starts it from inside the running session, and a watcher that stops it when
# xfce4-session exits so the next login starts clean.
install -Dpm644 %{_sourcedir}/xfce-session.target \
    %{buildroot}/usr/lib/systemd/user/xfce-session.target
install -Dpm644 %{_sourcedir}/xfce-session-watch.service \
    %{buildroot}/usr/lib/systemd/user/xfce-session-watch.service
install -Dpm644 %{_sourcedir}/xfce-graphical-session.desktop \
    %{buildroot}%{_sysconfdir}/xdg/autostart/xfce-graphical-session.desktop

# The GTK portal backend is activated by the systemd user manager and must
# open the X display itself; the manager does not inherit XAUTHORITY.
install -Dpm644 %{_sourcedir}/xdg-desktop-portal-gtk-x11.conf \
    %{buildroot}/usr/lib/systemd/user/xdg-desktop-portal-gtk.service.d/10-tenko-x11.conf

# New-user XFCE defaults.  The installer creates the admin account with
# "useradd -m", so these land in ~/.config on first login.  They are partial
# channel files on purpose: xfconf fills every unset property from the
# system-wide defaults.
cat > "$xfconfdir/xsettings.xml" <<'EOF'
<?xml version="1.1" encoding="UTF-8"?>

<channel name="xsettings" version="1.0">
  <property name="Net" type="empty">
    <property name="ThemeName" type="string" value="Arc-Dark"/>
    <property name="IconThemeName" type="string" value="kora"/>
    <property name="SoundThemeName" type="string" value="freedesktop"/>
  </property>
  <property name="Gtk" type="empty">
    <property name="DecorationLayout" type="string" value="icon,menu:minimize,maximize,close"/>
  </property>
  <property name="Xfce" type="empty">
    <property name="SyncThemes" type="bool" value="true"/>
  </property>
</channel>
EOF

cat > "$xfconfdir/xfwm4.xml" <<'EOF'
<?xml version="1.1" encoding="UTF-8"?>

<channel name="xfwm4" version="1.0">
  <property name="general" type="empty">
    <property name="theme" type="string" value="Arc-Dark"/>
  </property>
</channel>
EOF

cat > "$xfconfdir/xfce4-terminal.xml" <<'EOF'
<?xml version="1.1" encoding="UTF-8"?>

<channel name="xfce4-terminal" version="1.0">
  <property name="font-name" type="string" value="Terminus (TTF) Medium 12"/>
  <property name="color-foreground" type="string" value="#ffffff"/>
  <property name="color-background" type="string" value="#000000"/>
  <property name="color-background-vary" type="bool" value="false"/>
  <property name="color-cursor-use-default" type="bool" value="true"/>
  <property name="color-selection-use-default" type="bool" value="true"/>
  <property name="color-bold-use-default" type="bool" value="true"/>
  <property name="color-palette" type="string" value="#000000;#cc0000;#4e9a06;#c4a000;#3465a4;#75507b;#06989a;#d3d7cf;#555753;#ef2929;#8ae234;#fce94f;#739fcf;#ad7fa8;#34e2e2;#eeeeec"/>
  <property name="color-bold-is-bright" type="bool" value="true"/>
  <property name="color-use-theme" type="bool" value="false"/>
  <property name="tab-activity-color" type="string" value="#aa0000"/>
</channel>
EOF

# Panel layout.  Without this, xfce4-panel seeds ~/.config from
# /etc/xdg/xfce4/panel/default.xml on first login, which has a second panel
# at the bottom of the screen.  Ship the top panel only, carrying the same
# plugins as the upstream default panel-1 and no panel-2.
cat > "$xfconfdir/xfce4-panel.xml" <<'EOF'
<?xml version="1.1" encoding="UTF-8"?>

<channel name="xfce4-panel" version="1.0">
  <property name="configver" type="int" value="2"/>
  <property name="panels" type="array">
    <value type="int" value="1"/>
    <property name="dark-mode" type="bool" value="true"/>
    <property name="panel-1" type="empty">
      <property name="position" type="string" value="p=6;x=0;y=0"/>
      <property name="length" type="uint" value="100"/>
      <property name="position-locked" type="bool" value="true"/>
      <property name="icon-size" type="uint" value="16"/>
      <property name="size" type="uint" value="26"/>
      <property name="plugin-ids" type="array">
        <value type="int" value="1"/>
        <value type="int" value="2"/>
        <value type="int" value="3"/>
        <value type="int" value="4"/>
        <value type="int" value="5"/>
        <value type="int" value="6"/>
        <value type="int" value="7"/>
        <value type="int" value="8"/>
        <value type="int" value="9"/>
        <value type="int" value="10"/>
      </property>
    </property>
  </property>
  <property name="plugins" type="empty">
    <property name="plugin-1" type="string" value="applicationsmenu">
      <property name="button-title" type="string" value=""/>
      <property name="button-icon" type="string" value="desktop-environment-xfce"/>
    </property>
    <property name="plugin-2" type="string" value="tasklist">
      <property name="grouping" type="uint" value="1"/>
    </property>
    <property name="plugin-3" type="string" value="separator">
      <property name="expand" type="bool" value="true"/>
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-4" type="string" value="pager"/>
    <property name="plugin-5" type="string" value="separator">
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-6" type="string" value="systray">
      <property name="square-icons" type="bool" value="true"/>
    </property>
    <property name="plugin-7" type="string" value="separator">
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-8" type="string" value="clock"/>
    <property name="plugin-9" type="string" value="separator">
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-10" type="string" value="actions"/>
  </property>
</channel>
EOF

%files -f %{_sourcedir}/tenko-desktop-config.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 6-8
- Make Ristretto the default image viewer in /etc/xdg/mimeapps.list for
  every image type its desktop file handles: PNG, JPEG, GIF, WebP, BMP,
  TIFF, SVG, XPM and X pixmap.  mpv keeps the audio and video defaults.
  The file is %config(noreplace); an unmodified installed copy is replaced
  on upgrade, while a locally edited one is kept.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-7
- Give the systemd-activated xdg-desktop-portal-gtk service a DISPLAY and
  XAUTHORITY.  The user manager does not inherit the LightDM session's
  XAUTHORITY, so the GTK backend aborted with "cannot open display: :0.0"
  and every portal request timed out (issue #46).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-6
- Activate graphical-session.target in an XFCE session.  XFCE 4.20 does not
  start the session through systemd, so the target stayed inactive and
  xdg-desktop-portal.service, which has Requisite=graphical-session.target,
  refused every D-Bus activation (file choosers, OpenURI and Flatpak apps
  timed out).  Ship xfce-session.target (BindsTo=graphical-session.target),
  an /etc/xdg/autostart entry that exports DISPLAY/XAUTHORITY and starts it,
  and xfce-session-watch.service, which stops the target when xfce4-session
  exits.  Existing sessions get the fix at the next login (issue #48).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-5
- Set the default XSettings SoundThemeName to freedesktop so libcanberra
  resolves event sounds from the sound-theme-freedesktop package
  (issue #43).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-4
- Ship the desktop metadata defaults: /etc/xdg/mimeapps.list associates
  Thunar, Vim, mpv and the XFCE preferred browser, and maps help: URIs to
  the new tenko-help handler.  Install the Help System layout under
  /usr/share/help (tenko and C/tenko) with a fallback page and a
  /usr/share/applications/tenko-help.desktop entry (issue #35).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-3
- Ship a single top panel in /etc/skel/xfce4-panel.xml.  xfce4-panel was
  still seeding new accounts from /etc/xdg/xfce4/panel/default.xml, which
  brings up a second panel at the bottom of the screen.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-2
- Ship new-user XFCE defaults in /etc/skel: Arc-Dark GTK/Xfwm theme,
  Kora icons and the Terminus terminal profile.
- The desktop metas now require arc-theme, kora-icon-theme and
  font-terminus so the defaults resolve on a desktop install.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-1
- Rebase on the Tenko 6 distro release with Epoch 1 so installs carrying
  the old 13.1 EVR upgrade cleanly.
- Drop the browneye-desktop-config Obsoletes/Provides alias; no Browneye
  installs remain.

* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-2
- Rename browneye-desktop-config to tenko-desktop-config and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-1
- Initial X session configuration
