Name:       pango
Version:    1.58.2
Release:    5
Summary:    text layout library
License:    LGPL-2.1-or-later
URL:        https://www.gtk.org/docs/architecture/pango
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: fontconfig >= 2.13.1
BuildRequires: fribidi >= 1.0.13
BuildRequires: glib >= 2.76.4
BuildRequires: cairo
BuildRequires: freetype
BuildRequires: gobject-introspection
BuildRequires: harfbuzz
BuildRequires: libx11
BuildRequires: libxft
BuildRequires: libxrender

Provides: pkgconfig(pango)
Provides: pkgconfig(pangocairo)
Provides: pkgconfig(pangoft2)
%description
Pango is a library for laying out and rendering text

%prep
%setup -q

%build
mkdir build
pushd build
meson setup --prefix=/usr            \
            --buildtype=release      \
            --wrap-mode=nofallback   \
            -D introspection=enabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%package gir
Summary:    GObject Introspection data for pango
License:    LGPL-2.1-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for pango, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/pango.filelist
%files gir -f %{_sourcedir}/pango-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.58.2-5
- Record the verified license (LGPL-2.1-or-later): meson.build (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.58.2-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.58.2-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.58.2-2
- Split devel payload into pango-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.58.2
- Sync with 1.50.14

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.50.14-1
- Version bump
