Name:       libhandy
Version:    1.8.3
Release:    1
Summary:    GTK 3 widgets for adaptive user interfaces
License:    LGPL-2.1-or-later
URL:        https://gitlab.gnome.org/GNOME/libhandy
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: meson
BuildRequires: ninja
BuildRequires: gettext
BuildRequires: glib
BuildRequires: gtk+
BuildRequires: gobject-introspection
BuildRequires: vala

%description
libhandy provides GTK 3 widgets and objects for adaptive user interfaces
(header bars, preference windows, view switchers, leaflets).  Seahorse uses
it.  The package includes the GObject introspection data and the Vala
binding.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                  \
      --prefix=/usr             \
      --libdir=/usr/lib64       \
      --buildtype=release       \
      -Dintrospection=enabled   \
      -Dvapi=true               \
      -Dgtk_doc=false           \
      -Dtests=false             \
      -Dexamples=false          \
      -Dglade_catalog=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libhandy.filelist

%changelog
* Mon Nov 16 2026 tenko <build@tenko.invalid> 1.8.3-1
- New package, not in the base set: latest upstream stable release
  (1.8.3, checked 2026-11-16).  Required by Seahorse.
- Built with introspection and the Vala binding; without the demo, the
  tests, the API reference and the Glade catalog.
