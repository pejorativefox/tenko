Name:       gstreamer
Version:    1.28.8
Release:    3
Summary:    Streaming multimedia framework
License:    LGPL-2.1-or-later AND BSD-3-Clause
URL:        https://gstreamer.freedesktop.org/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: bash-completion
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
Streaming multimedia framework

%prep
%setup

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -D bash-completion=enabled \
      -D gst_debug=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/gstreamer.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 1.28.8-3
- Package the upstream gst-inspect-1.0/gst-launch-1.0 bash completions and
  the gst helper again.  They were dropped when the generated filelist was
  made in a build image without bash-completion.pc; require bash-completion
  and enable the option so a future build fails instead of losing them.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.28.8-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later AND BSD-3-Clause): COPYING, gst/gstplugin.c and gst/gstcpuid.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.28.8-1
- Sync with the base set

* Thu Sep 10 2020 Chris Statzer <chris.statzer@qq.com> 1.16.2
- Initial RPM

