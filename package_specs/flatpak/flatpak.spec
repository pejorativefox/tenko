Name:       flatpak
Version:    1.18.4
Release:    7
Summary:    Application sandboxing and distribution framework
License:    LGPL-2.1-or-later
URL:        https://flatpak.org/
Source0:    %{name}-%{version}.tar.xz
Requires:   bubblewrap
Requires:   xdg-dbus-proxy
Requires:   fuse3
Requires:   gnupg
# This build enables flatpak's dconf proxy, so sandboxed apps inherit the
# host's GSettings values.
Requires:   dconf
Prefix:     /usr
BuildRequires: appstream
BuildRequires: dconf
BuildRequires: fuse3
BuildRequires: gdk-pixbuf
BuildRequires: json-glib
BuildRequires: libostree
BuildRequires: libxau
BuildRequires: openssl
BuildRequires: polkit
BuildRequires: xorgproto
BuildRequires: libjpeg-turbo
BuildRequires: libpng
BuildRequires: shared-mime-info
BuildRequires: gobject-introspection
BuildRequires: python-pyparsing
BuildRequires: bubblewrap
BuildRequires: xdg-dbus-proxy

%description
Flatpak is a system for building, distributing and running sandboxed desktop
applications.  It provides the flatpak command, the session and system
helpers, and the bundled bwrap/dbus-proxy launchers.

Flatpak is not in the base set.  This spec tracks the current upstream
stable release; the dependency chain comes from the base set where a
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

# Let active local wheel users manage system-wide remotes without a polkit
# agent (issue #29).
install -Dpm0644 %{_sourcedir}/50-tenko-flatpak.rules \
    %{buildroot}/etc/polkit-1/rules.d/50-tenko-flatpak.rules

# Enable Flathub as a system remote out of the box.  flatpak only creates a
# remote from remotes.d when the repository does not already configure one,
# so an existing remote is left untouched.
install -Dpm0644 %{_sourcedir}/flathub.flatpakrepo \
    %{buildroot}/usr/share/flatpak/remotes.d/flathub.flatpakrepo

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
* Sun Nov 08 2026 tenko <build@tenko.invalid> 1.18.4-7
- Allow active local wheel users to configure system-wide flatpak remotes
  (org.freedesktop.Flatpak.configure-remote) and install local bundles
  (org.freedesktop.Flatpak.install-bundle), matching the upstream wheel
  rule for remote install/uninstall.  The base desktop has no polkit
  authentication agent, so remote-add previously failed with "Flatpak
  system operation ConfigureRemote not allowed for user" (issue #29).
- Ship /usr/share/flatpak/remotes.d/flathub.flatpakrepo so Flathub is
  available as a system remote out of the box.  An existing remote
  configuration is left untouched.
- Require dconf: this build enables the dconf proxy, so sandboxed apps
  inherit the host's GSettings values.

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
- Update from 1.5.1 (2019) to 1.18.4.  Flatpak is not in the base set;
  pinned to the current upstream stable release.  Uses the system bubblewrap
  and xdg-dbus-proxy instead of the offline subproject wraps; Wayland
  security-context support is disabled because the Browneye desktop is X11.
