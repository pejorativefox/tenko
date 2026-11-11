Name:       xfce4-screensaver
Version:    4.20.2
Release:    2
Summary:    Screensaver and session locker for Xfce
License:    GPL-2.0-or-later AND LGPL-2.1-or-later AND LGPL-2.0-or-later
URL:        https://docs.xfce.org/apps/xfce4-screensaver/start
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: gcc
BuildRequires: gettext
BuildRequires: meson
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: gtk+
BuildRequires: glib
BuildRequires: dbus-daemon
BuildRequires: dbus-glib
BuildRequires: xfconf
BuildRequires: libxfce4ui
BuildRequires: libxfce4util
BuildRequires: garcon
BuildRequires: libx11
BuildRequires: libxext
BuildRequires: libxscrnsaver
BuildRequires: libxklavier
BuildRequires: libwnck
BuildRequires: linux-pam
BuildRequires: systemd
BuildRequires: cairo
BuildRequires: dbus-libs
BuildRequires: gdk-pixbuf
BuildRequires: pango
BuildRequires: shared-mime-info
BuildRequires: xorgproto

Requires:   gtk+
Requires:   glib
Requires:   dbus-daemon
Requires:   dbus-glib
Requires:   xfconf
Requires:   libxfce4ui
Requires:   libxfce4util
Requires:   garcon
Requires:   libx11
Requires:   libxext
Requires:   libxscrnsaver
Requires:   libxklavier
Requires:   libwnck
Requires:   linux-pam
Requires:   systemd

%description
xfce4-screensaver is a screen saver and session-locking program for the Xfce
desktop.  It can lock the session automatically when the screen saver is
activated or when the system suspends, and it provides the
xfce4-screensaver-command interface used by the desktop's lock action.

%package lang
Summary:    xfce4-screensaver translations
Requires:   xfce4-screensaver = %{version}-%{release}

%description lang
Translations for xfce4-screensaver.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -Dx11=enabled       \
      -Dwayland=disabled  \
      -Ddocs=disabled     \
      -Dsession-manager=systemd
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/xfce4-screensaver.filelist

%files lang -f %{_sourcedir}/xfce4-screensaver-lang.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 4.20.2-2
- Require dbus-daemon instead of the nonexistent "dbus" binary package;
  the distro splits dbus into dbus-daemon, dbus-libs and dbus-x11.  The
  bad requirement made the package uninstallable (dbus-1.pc and the
  session bus both come from dbus-daemon).

* Wed Nov 11 2026 tenko <build@tenko.invalid> 4.20.2-1
- Initial package.  xfce4-screensaver is not in the base set.
- Version 4.20.2 is the latest stable upstream release (2026-03-02).
- Source: https://archive.xfce.org/src/apps/xfce4-screensaver/4.20/xfce4-screensaver-4.20.2.tar.xz
  md5 5354f83de438c739dbd43775a202672f
  sha256 5032f60a31df5e50a80512e301b595be5ea6a6bd762cdd95cacc24cbd29a01d7
- Build the X11 backend with PAM authentication and systemd-logind session
  tracking; the Wayland backend and XML documentation are disabled because
  the desktop session is X11-only and xmlto is not part of the build image.
- PAM service file is installed as /etc/pam.d/xfce4-screensaver.
