Name:       python3-gobject
Version:    3.58.1
Release:    2
Summary:    Python bindings for GObject Introspection
License:    LGPL-2.1-or-later
URL:        https://pygobject.gnome.org/
Source0:    pygobject-%{version}.tar.gz
Prefix:     /usr
BuildRequires: cairo
BuildRequires: glib
BuildRequires: libffi
BuildRequires: meson
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: python
Requires:   glib-gir
Provides:   python3-gobject-base = %{version}-%{release}

%description
PyGObject provides the gi Python package, which loads GObject
Introspection typelibs at run time and exposes the GObject, GLib and GIO
APIs to Python.  dbus-python's GLib main-loop integration and TuneD itself
need it.

This build disables the optional pycairo integration (-Dpycairo=disabled)
because Tenko does not ship pycairo; the GObject/GLib bindings used by
TuneD do not need it.

%prep
%setup -q -n pygobject-%{version}

%build
rm -rf build
meson setup build --prefix=/usr --buildtype=release \
    -Dpycairo=disabled -Dtests=false
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-gobject.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 3.58.1-2
- Rebuild with tenko-rpm-config 6-4 for the generated python(abi) = 3.15 requirement on its Python modules.

* Tue Nov 10 2026 tenko <build@tenko.invalid> 3.58.1-1
- New package: PyGObject 3.58.1 (latest stable upstream).  Not in the base
  set; dbus-python's GLib main loop and TuneD require the gi module.
- Build with pycairo disabled because Tenko does not package pycairo; the
  GObject/GLib bindings TuneD uses are unaffected.
