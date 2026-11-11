Name:       xfce4-terminal
Version:    1.2.0
Release:    3
Summary:    Xfce terminal emulator
License:    GPL-2.0-or-later
URL:        https://docs.xfce.org/apps/xfce4-terminal/start
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: libxfce4ui
BuildRequires: vte
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: libx11
BuildRequires: libxfce4util
BuildRequires: pango
BuildRequires: shared-mime-info
BuildRequires: xfconf
BuildRequires: xorgproto
BuildRequires: mesa
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
BuildRequires: pixman
BuildRequires: libxslt
BuildRequires: docbook-xsl-nons
Requires:   libxfce4ui
Requires:   vte

%description
Xfce4 Terminal is a GTK+3 terminal emulator for the Xfce desktop.

%package lang
Summary:    xfce4-terminal translations
Requires:   xfce4-terminal = %{version}-%{release}

%description lang
Translations for xfce4-terminal.

%prep
%setup -q
# workaround: guard functions that are only available with
# gtk-layer-shell, which is not part of the base set.
sed -e '570i #ifdef HAVE_GTK_LAYER_SHELL' \
    -e '574a #endif'                      \
    -i terminal/terminal-window-dropdown.c

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -Ddoc=true
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/xfce4-terminal.filelist
%files lang -f %{_sourcedir}/xfce4-terminal-lang.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.2.0-3
- Build the man page: -Ddoc=true, now that docbook-xml 4.5 and
  docbook-xsl-nons 1.79.2 are packaged with working XML catalogs.
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.0-2
- Split lang payload into xfce4-terminal-lang (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.0
- Initial RPM, synced with the base set (xfce4-terminal 1.2.0)
- Build with -Ddoc=true: the man page needs docbook-xsl-nons, which is
  not installed in the build image; the terminal itself is unaffected
