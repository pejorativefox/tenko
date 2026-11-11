Name:       glib
Version:    2.90.1
Release:    4
Summary:    Glib low level system libraries
License:    LGPL-2.1-or-later
URL:        https://gitlab.gnome.org/GNOME/glib
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
BuildRequires: bash-completion
BuildRequires: gobject-introspection
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

# Keep gschemas.compiled in sync with the schemas actually installed.  The
# cache is otherwise only written by whichever package compiled it at build
# time (gtk+ today), so schemas shipped later -- e.g. org.gnome.nm-applet
# from libnma -- never reach it and applications abort with
# "Settings schema ... is not installed".  File triggers fire for installs,
# upgrades and erasures in one transaction, including image installs that
# run scriptlets.
%transfiletriggerin -- %{_datadir}/glib-2.0/schemas
glib-compile-schemas %{_datadir}/glib-2.0/schemas &>/dev/null || :

%transfiletriggerpostun -- %{_datadir}/glib-2.0/schemas
glib-compile-schemas %{_datadir}/glib-2.0/schemas &>/dev/null || :

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
* Sun Nov 08 2026 browneye <build@browneye.invalid> 2.90.1-4
- Add GSettings schema file triggers so every transaction that installs,
  upgrades or erases a schema recompiles gschemas.compiled.  The cache
  owned by gtk+ did not include schemas installed later, so nm-applet
  aborted with "Settings schema 'org.gnome.nm-applet' is not installed"
  (issue #31).

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
