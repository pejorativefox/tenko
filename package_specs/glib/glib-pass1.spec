Name:       glib
Version:    2.90.0
Release:    1
Summary:    Glib low level system libraries (bootstrap pass, no introspection)
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
Bootstrap pass of GLib for building gobject-introspection.  It installs the
same libraries as the final glib package but no GObject Introspection data;
the final glib package is rebuilt afterwards with introspection enabled.
This package is only installed inside the throw-away build container.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                       \
      --prefix=/usr                  \
      --buildtype=release            \
      -D introspection=disabled      \
      -D glib_debug=disabled         \
      -D man-pages=enabled           \
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

%files -f %{_sourcedir}/glib-pass1.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.90.0-1
- Bootstrap pass of glib 2.90.0 without GObject Introspection, used to
  build gobject-introspection before the final glib package (E1 toolchain).
