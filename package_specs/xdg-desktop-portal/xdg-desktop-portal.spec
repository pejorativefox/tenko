Name:       xdg-desktop-portal
Version:    1.22.1
Release:    2
Summary:    Desktop integration portal 
License:    LGPL-2.1-or-later AND LGPL-2.0-or-later AND GPL-2.0-or-later
URL:        https://flatpak.github.io/xdg-desktop-portal/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: flatpak
BuildRequires: fuse3
BuildRequires: gdk-pixbuf
BuildRequires: gst-plugins-base
BuildRequires: gstreamer
BuildRequires: json-glib
BuildRequires: libgudev
BuildRequires: pipewire
BuildRequires: openssl
BuildRequires: shared-mime-info
BuildRequires: dconf
BuildRequires: libXdmcp
BuildRequires: libdrm
BuildRequires: libjpeg-turbo
BuildRequires: libostree
BuildRequires: libpciaccess
BuildRequires: libpng
BuildRequires: libx11
BuildRequires: libxau
BuildRequires: libxcb
BuildRequires: libxext
BuildRequires: libxfixes
BuildRequires: libxxf86vm
BuildRequires: mesa
BuildRequires: polkit
BuildRequires: xorgproto
BuildRequires: python3-docutils

%description
Desktop integration portal 

%prep
%setup

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -D tests=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/xdg-desktop-portal.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.22.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later AND LGPL-2.0-or-later AND GPL-2.0-or-later): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.22.1-1
- Sync with the base set

* Wed Jan 13 2021 Chris Statzer <chris.statzer@qq.com> 1.8.0
- Initial RPM

