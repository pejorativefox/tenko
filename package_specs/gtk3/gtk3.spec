Name:       gtk+
Version:    3.24.52
Release:    2
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    gtk-%{version}.tar.xz
Provides: pkgconfig(gdk-3.0), pkgconfig(gtk+-3.0)

%description
TODO

%prep
%setup -q -n gtk-%{version}

%build
mkdir build
pushd build
meson setup ..                     \
      --prefix=/usr                \
      --buildtype=release          \
      -D man=false                 \
      -D broadway_backend=true     \
      -D wayland_backend=false     \
      -D gtk_doc=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
glib-compile-schemas %{buildroot}/usr/share/glib-2.0/schemas || true
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/gtk3.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 3.24.52
- Sync with BLFS r13.1 (3.24.38)

# let's skip this for now

