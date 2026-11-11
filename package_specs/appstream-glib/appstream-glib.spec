Name:       appstream-glib
Version:    0.8.4
Release:    2
Summary:    Glib AppStream metadata support.
License:    LGPL-2.1-or-later AND GPL-2.0-or-later
URL:        https://github.com/hughsie/appstream-glib
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: cairo
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: json-glib
BuildRequires: openssl
BuildRequires: pango
BuildRequires: shared-mime-info
BuildRequires: at-spi2-core
BuildRequires: dbus-daemon
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
BuildRequires: pixman
BuildRequires: xorgproto
BuildRequires: gperf

%description
Glib AppStream metadata support.


%prep
%setup -n appstream-glib-%{version}

%build
mkdir build
pushd build
meson --prefix=/usr -Dgtk-doc=false -Dman=false ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/appstream-glib.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.8.4-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later AND GPL-2.0-or-later): COPYING and the SPDX headers in libappstream-glib/ and client/ (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.8.4-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.7.16
- Initial RPM

