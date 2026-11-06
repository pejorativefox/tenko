Name:       xinit
Version:    1.4.4
Release:    1
Summary:    X Window System initializer
License:    MIT
Prefix:     /usr
Source0:    xinit-1.4.4.tar.xz

%description
xinit and startx start an X server and a client session.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
mkdir -p %{buildroot}/etc/X11/xinit
cat > %{buildroot}/etc/X11/xinit/xinitrc <<'EOF'
#!/bin/sh
exec startxfce4
EOF
chmod 755 %{buildroot}/etc/X11/xinit/xinitrc

%files -f %{_sourcedir}/xinit.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.4.4-1
- Initial package
