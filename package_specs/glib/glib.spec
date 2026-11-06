Name:       glib
Version:    2.90.1
Release:    3
Summary:    Glib low level system libraries
License:    LGPL-2.1-or-later
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

%package lang
Summary:    glib translations
Requires:   glib = %{version}-%{release}

%description lang
Translations for glib.

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
License:    LGPL-2.1-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for glib, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/glib.filelist
%files lang -f %{_sourcedir}/glib-lang.filelist
%files gir -f %{_sourcedir}/glib-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.90.1-3
- Record the verified license (LGPL-2.1-or-later): COPYING and LICENSES/ (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.90.1-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.90.1-1
- Update to 2.90.1 (current upstream version).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.90.0-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.90.0-2
- Split lang, devel payload into glib-lang, glib-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.88.3
- Sync with 2.77.2

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 2.77.2
- Version bump 
