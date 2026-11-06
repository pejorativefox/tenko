Name:       tenko-desktop-config
Version:    13.1
Release:    2
# Tenko rename compatibility (issue #22).
Obsoletes: browneye-desktop-config < 13.1-2
Provides: browneye-desktop-config = %{version}-%{release}
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
* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-2
- Rename browneye-desktop-config to tenko-desktop-config and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-1
- Initial X session configuration
