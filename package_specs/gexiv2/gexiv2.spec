Name:       gexiv2
Version:    0.14.7
Release:    1
Summary:    GObject wrapper around the exiv2 metadata library
License:    GPL-2.0-or-later
URL:        https://gitlab.gnome.org/GNOME/gexiv2
Source0:    gexiv2-%{version}.tar.xz
Prefix:     /usr

BuildRequires: exiv2
BuildRequires: glib
BuildRequires: gobject-introspection

%description
gexiv2 is a GObject wrapper around the exiv2 C++ library, giving
GLib and GObject-introspected applications access to Exif, IPTC and
XMP image metadata.  GIMP 3 reads and writes metadata through it.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                  \
      --prefix=/usr             \
      --buildtype=release       \
      -D introspection=true     \
      -D vapi=false             \
      -D python3=false          \
      -D tools=false            \
      -D tests=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/gexiv2.filelist

%changelog
* Wed Nov 25 2026 tenko <build@tenko.invalid> 0.14.7-1
- New package, not in the base set: latest upstream stable release
  (0.14.7, checked 2026-11-25); GIMP 3 reads and writes image
  metadata through it.
- GObject introspection is enabled.  The vapi file, the gi Python
  overrides module and the command-line tool are not built: the tool
  is written in vala and requires the generated vapi.
