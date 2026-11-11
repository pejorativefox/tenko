Name:       libpeas
Version:    1.38.1
Release:    2
Summary:    libpeas is a GObject based plugins engine, and is targeted at giving every application the chance to assume its own extensibility. 
License:    LGPL-2.1-or-later
URL:        https://gitlab.gnome.org/GNOME/libpeas
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

Provides: pkgconfig(atk-2.0)
Provides: pkgconfig(atk)
BuildRequires: gobject-introspection
BuildRequires: gtk+
BuildRequires: luajit
BuildRequires: python3-gobject
BuildRequires: shared-mime-info
BuildRequires: xorgproto
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: dbus-daemon
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: fribidi
BuildRequires: gdk-pixbuf
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

%description
libpeas is a GObject based plugins engine, and is targeted at giving every application the chance to assume its own extensibility. 

%prep
%setup

%build
mkdir build
pushd build

meson setup --prefix=/usr          \
            --buildtype=release    \
            --wrap-mode=nofallback \
            -D python3=false       \
            ..
ninja
popd

%install    
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libpeas.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.38.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): COPYING and meson.build "license: LGPLv2.1+" (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.38.1-1
- Sync with upstream

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.26.0
- Initial RPM release
