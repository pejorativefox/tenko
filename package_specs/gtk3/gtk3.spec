Name:       gtk+
Version:    3.24.52
Release:    6
Summary:    Multi-platform toolkit for creating graphical user interfaces
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    gtk-%{version}.tar.xz

Provides: pkgconfig(gdk-3.0), pkgconfig(gtk+-3.0)
%description
GTK is a multi-platform toolkit for creating graphical user interfaces. It
offers a complete set of widgets and is suitable for projects ranging from
small one-off projects to complete application suites.

%package lang
Summary:    gtk+ translations
Requires:   gtk+ = %{version}-%{release}

%description lang
Translations for gtk+.

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

%package gir
Summary:    GObject Introspection data for gtk+
License:    LGPL-2.1-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for gtk+, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/gtk3.filelist
%files lang -f %{_sourcedir}/gtk3-lang.filelist
%files gir -f %{_sourcedir}/gtk3-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.24.52-6
- Replace the TODO summary/description and record the verified license
  (LGPL-2.1-or-later): meson.build, gdk/COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.24.52-5
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.24.52-4
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.24.52-3
- Split lang, devel payload into gtk+-lang, gtk+-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 3.24.52
- Sync with BLFS r13.1 (3.24.38)

# let's skip this for now

