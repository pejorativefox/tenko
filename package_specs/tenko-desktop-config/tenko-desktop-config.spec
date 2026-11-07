Name:       tenko-desktop-config
Version:    6
Release:    1
Epoch:      1
Summary:    Tenko X11/XFCE session configuration
License:    MIT
Prefix:     /usr

Requires:   xinit
Requires:   xfce4-session

%description
Default X session configuration for Tenko: startxfce4 on startx.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc/skel %{buildroot}/var/lib/xkb
cat > %{buildroot}/etc/skel/.xinitrc <<'EOF'
#!/bin/sh
exec startxfce4
EOF
chmod 644 %{buildroot}/etc/skel/.xinitrc

%files
%dir /var/lib/xkb
%config /etc/skel/.xinitrc

%changelog
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
