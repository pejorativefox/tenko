Name:       xfce-polkit
Version:    0.3
Release:    1
Summary:    PolicyKit authentication agent for XFCE
License:    GPL-2.0-only
URL:        https://github.com/ncopa/xfce-polkit
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

Requires:   polkit
Requires:   libxfce4ui
BuildRequires: gtk+, polkit, libxfce4ui, glib
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: harfbuzz
BuildRequires: libxfce4util
BuildRequires: pango
BuildRequires: shared-mime-info
BuildRequires: xorgproto
BuildRequires: dbus-daemon
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: fribidi
BuildRequires: libXdmcp
BuildRequires: libdrm
BuildRequires: libepoxy
BuildRequires: libjpeg-turbo
BuildRequires: liblzo2
BuildRequires: libpciaccess
BuildRequires: libpng
BuildRequires: libx11
BuildRequires: libxau
BuildRequires: libxcb
BuildRequires: libxcomposite
BuildRequires: libxcursor
BuildRequires: libxdamage
BuildRequires: libxext
BuildRequires: libxfixes
BuildRequires: libxft
BuildRequires: libxi
BuildRequires: libxinerama
BuildRequires: libxrandr
BuildRequires: libxrender
BuildRequires: libxres
BuildRequires: libxtst
BuildRequires: libxxf86vm
BuildRequires: mesa
BuildRequires: pixman
BuildRequires: xfconf

%description
A small PolicyKit authentication agent that integrates with the XFCE
desktop.  It listens on the session bus and shows the authentication dialog
when an application asks polkit for an administrative action.

Tenko ships it so applications can prompt for credentials: without an agent
every auth_admin polkit action (flatpak system remotes, NetworkManager
system connections, and so on) fails immediately.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/xfce-polkit.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 0.3-1
- New package: the XFCE polkit authentication agent.  Without an agent the
  base desktop could not answer auth_admin prompts, so flatpak remote-add
  failed with "ConfigureRemote not allowed for user" (issue #29).
- Version 0.3 is the latest upstream stable release (2018).  Upstream master
  only carries build fixes, not a newer release; this release builds against
  the packaged libxfce4ui and polkit 128.
