Name:       gtk2+
Version:    2.24.33
Release:    2
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    gtk+-%{version}.tar.xz
Provides: pkgconfig(gtk+-2.0)

%description
TODO

%prep
%setup -q -n gtk+-%{version}

%build
export CFLAGS="${CFLAGS:-} -Wno-error=incompatible-pointer-types -Wno-error=int-conversion -Wno-error=implicit-int -Wno-error=implicit-function-declaration"
sed -e 's#l \(gtk-.*\).sgml#& -o \1#' \
    -i docs/{faq,tutorial}/Makefile.in
%configure --sysconfdir=/etc
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
mv %{buildroot}/usr/bin/gtk-update-icon-cache %{buildroot}/usr/bin/gtk2-update-icon-cache
mkdir -pv %{buildroot}/etc/gtk-2.0/
cat > %{buildroot}/etc/gtk-2.0/gtkrc << "EOF"
include "/usr/share/themes/Clearlooks/gtk-2.0/gtkrc"
gtk-icon-theme-name = "elementary"
EOF

%files -f %{_sourcedir}/gtk2.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.24.33
- Sync with BLFS r13.1 (2.24.32)

# let's skip this for now

