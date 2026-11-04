Name:       flatpak
Version:    1.18.4
Release:    2
Summary:    Application sandboxing and distribution framework
License:    LGPL
Source0:    %{name}-%{version}.tar.xz
Requires:   bubblewrap
Requires:   xdg-dbus-proxy
Requires:   fuse3
Requires:   gnupg
Prefix:     /usr

%description
Flatpak is a system for building, distributing and running sandboxed desktop
applications.  It provides the flatpak command, the session and system
helpers, and the bundled bwrap/dbus-proxy launchers.

Flatpak is not in the BLFS r13.1 book.  This spec tracks the current upstream
stable release; the dependency chain comes from BLFS where the book has a
page, and from upstream for libostree.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                     \
      --prefix=/usr                 \
      --buildtype=release           \
      -Dman=disabled                \
      -Dgtkdoc=disabled             \
      -Ddocbook_docs=disabled       \
      -Dtests=false                 \
      -Dsystem_helper=enabled       \
      -Dseccomp=enabled             \
      -Dgir=enabled                 \
      -Dmalcontent=disabled         \
      -Ddconf=auto                  \
      -Dwayland_security_context=disabled \
      -Dxauth=enabled               \
      -Dlibzstd=enabled             \
      -Dsystemd=enabled             \
      -Dsystem_bubblewrap=/usr/bin/bwrap \
      -Dsystem_dbus_proxy=/usr/bin/xdg-dbus-proxy
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/flatpak.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.18.4-2
- Require gnupg.  gpgme finds the OpenPGP engine at runtime; without it
  gpgme reports "Invalid crypto engine" and flatpak remote-add fails
  before it can even set up the remote keyring.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.18.4-1
- Update from 1.5.1 (2019) to 1.18.4.  Flatpak is not in BLFS r13.1;
  pinned to the current upstream stable release.  Uses the system bubblewrap
  and xdg-dbus-proxy instead of the offline subproject wraps; Wayland
  security-context support is disabled because the Browneye desktop is X11.
