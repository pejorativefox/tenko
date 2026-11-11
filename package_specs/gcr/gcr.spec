Name:       gcr
Version:    3.41.2
Release:    1
Summary:    GNOME crypto services library and object framework
License:    LGPL-2.1
URL:        https://gitlab.gnome.org/GNOME/gcr
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: libgcrypt
BuildRequires: p11-kit
BuildRequires: pango
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
BuildRequires: pixman
BuildRequires: shared-mime-info
BuildRequires: xorgproto
BuildRequires: gnupg
BuildRequires: libsecret
BuildRequires: openssh
BuildRequires: gobject-introspection

%description
GCR is a library for displaying certificates and crypto UI, and accessing
key stores.  It also provides the viewer for crypto files on the GNOME
desktop.

%prep
%setup -q
sed -i 's:"/desktop:"/org:' schema/*.xml

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -D gtk_doc=false    \
      -D ssh_agent=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/gcr.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.41.2-1
- New package, required by libnma
