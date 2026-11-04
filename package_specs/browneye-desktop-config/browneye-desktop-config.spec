Name:       browneye-desktop-config
Version:    13.1
Release:    1
Summary:    Browneye X11/XFCE session configuration
License:    MIT
Prefix:     /usr

Requires:   xinit
Requires:   xfce4-session

%description
Default X session configuration for Browneye: startxfce4 on startx.

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
* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-1
- Initial X session configuration
