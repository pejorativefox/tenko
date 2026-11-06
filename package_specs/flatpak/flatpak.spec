Name:       flatpak
Version:    1.18.4
Release:    6
Summary:    Application sandboxing and distribution framework
License:    LGPL-2.1-or-later
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

%post
# Make the system-helper user available immediately.  The Tenko systemd
# package does not ship a sysusers.d file trigger, so packages that own a
# sysusers file must materialise it themselves (same pattern as openssh and
# privoxy).  Without this, revokefs fails with "User flatpak does not exist
# in password file entry" until the next boot.
if [ -x /usr/bin/systemd-sysusers ]; then
    /usr/bin/systemd-sysusers /usr/lib/sysusers.d/flatpak.conf || :
fi

%files -f %{_sourcedir}/flatpak.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.18.4-6
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING and the per-file SPDX headers (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.18.4-5
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.18.4-3
- Run systemd-sysusers in %post so the flatpak system-helper user exists
  immediately after installation.  The systemd package has no sysusers.d
  file trigger, so revokefs previously failed with "User flatpak does not
  exist in password file entry" until the next boot.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.18.4-2
- Require gnupg.  gpgme finds the OpenPGP engine at runtime; without it
  gpgme reports "Invalid crypto engine" and flatpak remote-add fails
  before it can even set up the remote keyring.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.18.4-1
- Update from 1.5.1 (2019) to 1.18.4.  Flatpak is not in BLFS r13.1;
  pinned to the current upstream stable release.  Uses the system bubblewrap
  and xdg-dbus-proxy instead of the offline subproject wraps; Wayland
  security-context support is disabled because the Browneye desktop is X11.
