Name:       light-locker
Version:    1.8.0
Release:    1
Summary:    Simple session locker for LightDM
License:    GPL-2.0-or-later
URL:        https://github.com/the-cavalry/light-locker
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: gcc
BuildRequires: make
BuildRequires: pkgconf
BuildRequires: gettext
BuildRequires: intltool
BuildRequires: xml-parser
BuildRequires: glib
BuildRequires: gtk+
BuildRequires: dbus-glib
BuildRequires: libx11
BuildRequires: libxext
BuildRequires: systemd
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: dbus-daemon
BuildRequires: dbus-libs
BuildRequires: gdk-pixbuf
BuildRequires: harfbuzz
BuildRequires: libice
BuildRequires: libsm
BuildRequires: libxscrnsaver
BuildRequires: libxxf86vm
BuildRequires: pango
BuildRequires: shared-mime-info
BuildRequires: xorgproto

Requires:   glib
Requires:   gtk+
Requires:   dbus-glib
Requires:   libx11
Requires:   libxext
Requires:   systemd

%description
light-locker is a simple session locker for the Xfce desktop.  It locks the
X11 session on demand, after the screen saver activates, on lid close and on
suspend, and integrates with LightDM to present the unlock screen.

%package lang
Summary:    light-locker translations
Requires:   light-locker = %{version}-%{release}

%description lang
Translations for light-locker.

%prep
%setup -q

%build
%configure \
    --with-systemd \
    --without-console-kit \
    --with-upower \
    --with-mit-ext \
    --with-dpms-ext \
    --disable-maintainer-mode
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/light-locker.filelist

%files lang -f %{_sourcedir}/light-locker-lang.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 1.8.0-1
- Initial package.  light-locker is not in the base set.
- Version 1.8.0 is the latest stable upstream release (2017-07-24); the
  project has not published a newer release.
- Source: https://github.com/the-cavalry/light-locker/releases/download/v1.8.0/light-locker-1.8.0.tar.bz2
  md5 d4820463ea99136511bdaedc08574c86
  sha256 3c76106f40a8efe67b462061e4c798e3e501b54356c8cdc1b67a3022d9d7dba1
- Build against GTK+ 3, systemd-logind and UPower, with the MIT-SCREEN-SAVER
  and DPMS extensions enabled.  ConsoleKit support is disabled because Tenko
  uses logind.
