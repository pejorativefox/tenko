Name:       gst-plugins-base
Version:    1.28.8
Release:    2
Summary:    Base gstreamer plugins
License:    LGPL-2.1-or-later AND BSD-3-Clause
URL:        https://gstreamer.freedesktop.org/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: alsa-lib
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: gstreamer
BuildRequires: gtk+
BuildRequires: libdrm
BuildRequires: libgudev
BuildRequires: libjpeg-turbo
BuildRequires: libogg
BuildRequires: libpng
BuildRequires: libvorbis
BuildRequires: libx11
BuildRequires: libxcb
BuildRequires: libxext
BuildRequires: libxi
BuildRequires: libxv
BuildRequires: mesa
BuildRequires: pango
BuildRequires: gobject-introspection
BuildRequires: iso-codes
BuildRequires: libopus
BuildRequires: libtheora
BuildRequires: sdl2
BuildRequires: shared-mime-info
BuildRequires: wayland
BuildRequires: at-spi2-core
BuildRequires: dbus-daemon
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: fribidi
BuildRequires: harfbuzz
BuildRequires: libXdmcp
BuildRequires: libepoxy
BuildRequires: liblzo2
BuildRequires: libpciaccess
BuildRequires: libxau
BuildRequires: libxcomposite
BuildRequires: libxcursor
BuildRequires: libxdamage
BuildRequires: libxfixes
BuildRequires: libxft
BuildRequires: libxinerama
BuildRequires: libxrandr
BuildRequires: libxrender
BuildRequires: libxres
BuildRequires: libxtst
BuildRequires: libxxf86vm
BuildRequires: pixman
BuildRequires: xorgproto

%description
Base gstreamer plugins

%prep
%setup

%build
mkdir build
pushd build
meson setup ..               \
      --prefix=/usr          \
      --buildtype=release    \
      --wrap-mode=nodownload
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/gst-plugins-base.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.28.8-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later AND BSD-3-Clause): COPYING and gst-libs/gst/fft/kiss_fft_f32.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.28.8-1
- Sync with the base set

* Thu Sep 10 2020 Chris Statzer <chris.statzer@qq.com> 1.16.2
- Initial RPM

