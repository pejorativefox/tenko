Name:       libportal 
Version:    0.9.1
Release:    2
Summary:    Flatpak portal library 
License:    LGPL-3.0-only
URL:        https://github.com/flatpak/libportal
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: gobject-introspection
BuildRequires: gtk+
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
Flatpak portal library 

%prep
%setup

%build
mkdir build
pushd build
meson setup ..                 \
      --prefix=/usr            \
      --buildtype=release      \
      -D backend-gtk4=disabled \
      -D backend-qt5=disabled  \
      -D backend-qt6=disabled  \
      -D docs=false            \
      -D vapi=false            \
      -D tests=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libportal.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.9.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-3.0-only): COPYING, LGPL v3, and the SPDX headers in libportal/*.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.9.1-1
- Sync with the base set

* Tue Jan 19 2021 Chris Statzer <chris.statzer@qq.com> 0.3
- Initial RPM

