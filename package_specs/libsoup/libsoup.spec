Name:       libsoup
Version:    2.74.3
Release:    1
Summary:    The libsoup is a HTTP client/server library for GNOME.
License:    LGPL-2.0-or-later
URL:        https://gitlab.gnome.org/GNOME/libsoup
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: glib2
BuildRequires: libxml2
BuildRequires: libpsl
BuildRequires: brotli
BuildRequires: gnutls
BuildRequires: glib-networking

%description
The libsoup is a HTTP client/server library for GNOME.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup --prefix=/usr --libdir=/usr/lib64 \
       --buildtype=release               \
       -Dgnome=true                      \
       -Dtests=false                     \
       -Dinstalled_tests=false           \
       -Dgtk_doc=false                   \
       -Dvapi=disabled                   \
       -Dgssapi=disabled                 \
       -Dsysprof=disabled                \
       -Dbrotli=enabled                  \
       -Dtls_check=true                  \
       ..
ninja
popd

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install

%files -f %{_sourcedir}/libsoup.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.74.3-1
- Update 2.62.3 -> 2.74.3, the final release of the libsoup 2.x line.
- Basis: libsoup3 is the active package; the archived libsoup 2.x
  release is 2.74.3, which is the newest 2.x release.  This spec
  stays on the 2.x ABI (libsoup-2.4) because the tree still ships
  consumers of it.
- Source: https://download.gnome.org/sources/libsoup/2.74/libsoup-2.74.3.tar.xz
  md5 8f657fd301a213629204b3320c35d75a
- Replaced autotools with the upstream Meson build (invoked as
  "meson setup"/"ninja" because the build image has no meson RPM
  macros).  TLS comes through glib-networking (built with gnutls);
  libpsl is a hard dependency and brotli decompression is enabled.
  Tests, gtk-doc and Vala bindings are disabled; GObject
  introspection stays at its auto default.
- Static filelist generated from the install tree.
