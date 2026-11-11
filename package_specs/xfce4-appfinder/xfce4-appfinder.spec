Name:       xfce4-appfinder
Version:    4.20.0
Release:    3
Summary:    An application finder for Xfce
License:    GPL-2.0-or-later
URL:        https://docs.xfce.org/xfce/xfce4-appfinder/start
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr
BuildRequires: cairo
BuildRequires: garcon
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: libxfce4ui
BuildRequires: libxfce4util
BuildRequires: xfconf
BuildRequires: at-spi2-core
BuildRequires: dbus-daemon
BuildRequires: fontconfig
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
BuildRequires: pango
BuildRequires: pixman
BuildRequires: shared-mime-info
BuildRequires: xorgproto

%description
An application finder for Xfce

%package lang
Summary:    xfce4-appfinder translations
Requires:   xfce4-appfinder = %{version}-%{release}

%description lang
Translations for xfce4-appfinder.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfce4-appfinder.filelist
%files lang -f %{_sourcedir}/xfce4-appfinder-lang.filelist


%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.0-3
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.0-2
- Split lang payload into xfce4-appfinder-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with 4.19.0

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.0
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

