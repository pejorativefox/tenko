Name:       glib
Version:    2.90.0
Release:    3
Summary:    Glib low level system libraries
License:    GPL3
Prefix:     /usr

%{!?glib_introspection:%global glib_introspection enabled}
Source0:    %{name}-%{version}.tar.xz

%description
GLib is a bundle of three low-level system libraries written in C and developed mainly by GNOME.

%package lang
Summary:    glib translations
Requires:   glib = %{version}-%{release}

%description lang
Translations for glib.

%package devel
Summary:    glib development files
Requires:   %{name}-gir = %{version}-%{release}
Requires:   glib = %{version}-%{release}
Provides:   pkgconfig(glib-2.0)
Provides:   pkgconfig(gobject-2.0)
Provides:   pkgconfig(gmodule-2.0)
Provides:   pkgconfig(gmodule-no-export-2.0)
Provides:   pkgconfig(gio-unix-2.0)
Provides:   pkgconfig(gio-2.0)
Provides:   pkgconfig(gthread-2.0)

%description devel
Development files for glib.

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
      -D man-pages=enabled            \
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


%package gir
Summary:    GObject Introspection data for glib
License:    GPL3
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for glib, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the -devel package.

%files -f %{_sourcedir}/glib.filelist
%files lang -f %{_sourcedir}/glib-lang.filelist
%files devel -f %{_sourcedir}/glib-devel.filelist
%files gir -f %{_sourcedir}/glib-gir.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.90.0-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.90.0-2
- Split lang, devel payload into glib-lang, glib-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.88.3
- Sync with BLFS r13.1 (2.77.2)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 2.77.2
- Version bump 
