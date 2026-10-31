Name:       glib
Version:    2.88.3
Release:    1
Summary:    Glib low level system libraries
License:    GPL3
Prefix:     /usr

%{!?glib_introspection:%global glib_introspection enabled}
Source0:    %{name}-%{version}.tar.xz
Provides:   pkgconfig(glib-2.0)
Provides:   pkgconfig(gobject-2.0)
Provides:   pkgconfig(gmodule-2.0)
Provides:   pkgconfig(gmodule-no-export-2.0)
Provides:   pkgconfig(gio-unix-2.0)
Provides:   pkgconfig(gio-2.0)
Provides:   pkgconfig(gthread-2.0)

%description
GLib is a bundle of three low-level system libraries written in C and developed mainly by GNOME.

%prep
%setup -a 0

%build
mkdir build
pushd build
meson setup ..                       \
      --prefix=/usr                  \
      --buildtype=release            \
      -D introspection=%{glib_introspection} \
      -D glib_debug=disabled         \
      -D man-pages=disabled           \
      -D sysprof=disabled            \
      -D selinux=disabled            \
      -D tests=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/glib.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.88.3
- Sync with BLFS r13.1 (2.77.2)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 2.77.2
- Version bump 
