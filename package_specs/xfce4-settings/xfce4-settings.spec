Name:       xfce4-settings
Version:    4.20.5
Release:    3
Summary:    Settings manager of the Xfce desktop
License:    GPL-2.0-or-later AND GPL-2.0-only AND LGPL-2.0-or-later
URL:        https://docs.xfce.org/xfce/xfce4-settings/start
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: exo
BuildRequires: fontconfig
BuildRequires: garcon
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: libnotify
BuildRequires: libx11
BuildRequires: libxcursor
BuildRequires: libxext
BuildRequires: libxfce4ui
BuildRequires: libxfce4util
BuildRequires: libxi
BuildRequires: libxklavier
BuildRequires: libxrandr
BuildRequires: pango
BuildRequires: xfconf
BuildRequires: dbus-daemon
BuildRequires: freetype
BuildRequires: fribidi
BuildRequires: harfbuzz
BuildRequires: libXdmcp
BuildRequires: libdrm
BuildRequires: libepoxy
BuildRequires: libjpeg-turbo
BuildRequires: liblzo2
BuildRequires: libpciaccess
BuildRequires: libpng
BuildRequires: libxau
BuildRequires: libxcb
BuildRequires: libxcomposite
BuildRequires: libxdamage
BuildRequires: libxfixes
BuildRequires: libxft
BuildRequires: libxinerama
BuildRequires: libxrender
BuildRequires: libxres
BuildRequires: libxtst
BuildRequires: libxxf86vm
BuildRequires: mesa
BuildRequires: pixman
BuildRequires: shared-mime-info
BuildRequires: xorgproto

%description
Settings manager of the Xfce desktop

%package lang
Summary:    xfce4-settings translations
Requires:   xfce4-settings = %{version}-%{release}

%description lang
Translations for xfce4-settings.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfce4-settings.filelist
%files lang -f %{_sourcedir}/xfce4-settings-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.5-3
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND GPL-2.0-only AND LGPL-2.0-or-later): COPYING (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.5-2
- Split lang payload into xfce4-settings-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.5
- Sync with 4.19.0

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

