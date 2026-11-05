Name:       gdk-pixbuf
Version:    2.44.8
Release:    6
Summary:    Image loading library
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

Provides: pkgconfig(gdk-pixbuf-2.0)
%description
GdkPixbuf is a library that loads image data in various formats and stores it as linear buffers in memory.

%package lang
Summary:    gdk-pixbuf translations
Requires:   gdk-pixbuf = %{version}-%{release}

%description lang
Translations for gdk-pixbuf.

%package tests
Summary:    gdk-pixbuf tests
Requires:   gdk-pixbuf = %{version}-%{release}

%description tests
Test suite and test data for gdk-pixbuf.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                \
      --prefix=/usr           \
      --buildtype=release     \
      -D png=enabled          \
      -D gif=disabled         \
      -D jpeg=enabled        \
      -D tiff=disabled        \
      -D thumbnailer=disabled \
      -D glycin=disabled      \
      -D man=false           \
      --wrap-mode=nofallback
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%package gir
Summary:    GObject Introspection data for gdk-pixbuf
License:    LGPL-2.1-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for gdk-pixbuf, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/gdk-pixbuf.filelist
%files lang -f %{_sourcedir}/gdk-pixbuf-lang.filelist
%files tests -f %{_sourcedir}/gdk-pixbuf-tests.filelist
%files gir -f %{_sourcedir}/gdk-pixbuf-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.44.8-6
- Record the verified license (LGPL-2.1-or-later): COPYING and meson.build (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.44.8-5
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).
- Rebuild with the .pc Requires exclusion so gdk-pixbuf-2.0.pc does not
  pull shared-mime-info/libxml2 into a runtime install.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.44.8-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.44.8-2
- Split lang, tests, devel payload into gdk-pixbuf-lang, gdk-pixbuf-tests, gdk-pixbuf-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.44.7
- Sync with BLFS r13.1 (2.42.9)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 2.42.9
- Version bump
