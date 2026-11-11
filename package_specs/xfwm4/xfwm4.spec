Name:       xfwm4
Version:    4.20.0
Release:    5
Summary:    Xfce's window manager
License:    GPL-2.0-or-later
URL:        https://docs.xfce.org/xfce/xfwm4/start
Source0:    %{name}-%{version}.tar.bz2
Patch0:     xfwm4-4.20.0-workspace-flash.patch
Prefix:     /usr

BuildRequires: libxpresent
BuildRequires: xorgproto
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: harfbuzz
BuildRequires: libepoxy
BuildRequires: libice
BuildRequires: libsm
BuildRequires: libwnck
BuildRequires: libx11
BuildRequires: libxcomposite
BuildRequires: libxdamage
BuildRequires: libxext
BuildRequires: libxfce4ui
BuildRequires: libxfce4util
BuildRequires: libxfixes
BuildRequires: libxinerama
BuildRequires: libxrandr
BuildRequires: libxrender
BuildRequires: libxres
BuildRequires: pango
BuildRequires: startup-notification
BuildRequires: xfconf
BuildRequires: dbus-daemon
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: fribidi
BuildRequires: libXdmcp
BuildRequires: libdrm
BuildRequires: libjpeg-turbo
BuildRequires: liblzo2
BuildRequires: libpciaccess
BuildRequires: libpng
BuildRequires: libxau
BuildRequires: libxcb
BuildRequires: libxcursor
BuildRequires: libxft
BuildRequires: libxi
BuildRequires: libxtst
BuildRequires: libxxf86vm
BuildRequires: mesa
BuildRequires: pixman
BuildRequires: shared-mime-info

%description
Xfce's window manager

%package lang
Summary:    xfwm4 translations
Requires:   xfwm4 = %{version}-%{release}

%description lang
Translations for xfwm4.

%prep
%setup
%patch -P 0 -p1

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfwm4.filelist
%files lang -f %{_sourcedir}/xfwm4-lang.filelist


%changelog
* Mon Nov 09 2026 tenko <build@tenko.invalid> 4.20.0-5
- Add xfwm4-4.20.0-workspace-flash.patch: keep the outgoing workspace's
  windows mapped until the incoming windows have painted (tracked with
  XDamage on the client windows), so switching workspaces no longer flashes
  the root wallpaper for a frame (upstream issue #314).  Fallback timeout is
  100 ms and the old immediate behaviour is kept when the compositor is
  inactive.

* Mon Nov 09 2026 tenko <build@tenko.invalid> 4.20.0-4
- Build with libXpresent (plus presentproto from xorgproto) so the compositor
  offers the XPresent vblank method.  Upstream enables it by default when
  pkg-config finds xpresent; the previous build image lacked it.
- Rebuild of the same upstream version: no source change.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.0-3
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.0-2
- Split lang payload into xfwm4-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with 4.18.0

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.18.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

