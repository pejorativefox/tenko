Name:       rofi
Version:    2.0.0
Release:    1
Summary:    Rofi application launcher.
License:    MIT
URL:        https://github.com/davatorium/rofi
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: meson
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: glib
BuildRequires: pango
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: libxkbcommon
BuildRequires: libxcb
BuildRequires: xcb-util
BuildRequires: xcb-util-image
BuildRequires: xcb-util-keysyms
BuildRequires: xcb-util-renderutil
BuildRequires: xcb-util-wm
BuildRequires: xcb-util-cursor
BuildRequires: xcb-util-xrm
BuildRequires: startup-notification
BuildRequires: xorgproto
BuildRequires: shared-mime-info
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: fribidi
BuildRequires: harfbuzz
BuildRequires: libXdmcp
BuildRequires: libjpeg-turbo
BuildRequires: liblzo2
BuildRequires: libpng
BuildRequires: libx11
BuildRequires: libxau
BuildRequires: libxext
BuildRequires: libxft
BuildRequires: libxrender
BuildRequires: pixman

%description
Rofi application launcher
Rofi is a window switcher, application launcher and dmenu replacement.

%prep
%setup -q

%build
meson setup build \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --buildtype=release \
    -Dwayland=disabled \
    -Dxcb=enabled \
    -Dimdkit=false \
    -Dcheck=disabled
ninja -C build

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install

%files -f %{_sourcedir}/rofi.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.0.0-1
- Not in the base set: bump to the latest upstream
  stable release (2.0.0, checked 2026-11-05). The 2.0 rewrite uses
  meson; build the XCB backend only (no Wayland stack in the repo).

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.5.4
- Initial RPM
