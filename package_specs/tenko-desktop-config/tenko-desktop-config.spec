Name:       tenko-desktop-config
Version:    6
Release:    2
Epoch:      1
Summary:    Tenko X11/XFCE session configuration
License:    MIT
Prefix:     /usr

Requires:   xinit
Requires:   xfce4-session

%description
Default X session configuration for Tenko: startxfce4 on startx, plus the
default XFCE look (GTK/icon/Xfwm themes and the terminal profile) for new
users.  The desktop metas pull in the themes and font these defaults name.

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

%files
%dir /var/lib/xkb
%config /etc/skel/.xinitrc
%dir %{_sysconfdir}/skel/.config
%dir %{_sysconfdir}/skel/.config/xfce4
%dir %{_sysconfdir}/skel/.config/xfce4/xfconf
%dir %{_sysconfdir}/skel/.config/xfce4/xfconf/xfce-perchannel-xml
%config(noreplace) %{_sysconfdir}/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml
%config(noreplace) %{_sysconfdir}/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml
%config(noreplace) %{_sysconfdir}/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-terminal.xml

%changelog
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
