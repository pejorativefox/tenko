Name:       lightdm-gtk-greeter
Version:    2.0.9
Release:    3
Summary:    GTK+ greeter for LightDM
License:    GPL-3.0-or-later
URL:        https://github.com/Xubuntu/lightdm-gtk-greeter
Source0:    lightdm-gtk-greeter-2.0.9.tar.gz
Source1:    lightdm-gtk-greeter.conf
Prefix:     /usr

BuildRequires: gtk+, libxklavier, gettext
# liblightdm-gobject-1.pc, the GIR and the headers come from lightdm.
BuildRequires: lightdm
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: harfbuzz
BuildRequires: libx11
BuildRequires: pango
BuildRequires: shared-mime-info
BuildRequires: xorgproto
BuildRequires: dbus-daemon
BuildRequires: fontconfig
BuildRequires: freetype
BuildRequires: fribidi
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
BuildRequires: mesa
BuildRequires: pixman

Requires: lightdm >= 1.19.2
# The Tenko greeter configuration names the desktop themes, so keep them
# resolvable on any install that brings in the greeter.
Requires: arc-theme
Requires: kora-icon-theme

%description
The reference GTK+ greeter for LightDM.  It provides the login screen, the
session/desktop chooser, the keyboard layout menu, and a power menu.

%package lang
Summary:    lightdm-gtk-greeter translations
Requires:   lightdm-gtk-greeter = %{version}-%{release}

%description lang
Translations for the LightDM GTK greeter.

%package doc
Summary:    lightdm-gtk-greeter documentation
Requires:   lightdm-gtk-greeter = %{version}-%{release}

%description doc
Sample greeter stylesheet.

%prep
%setup -q

%build
%configure \
    --libexecdir=/usr/lib/lightdm \
    --sbindir=%{_bindir} \
    --sysconfdir=/etc \
    --with-libxklavier \
    --enable-kill-on-sigterm \
    --disable-libido \
    --disable-libindicator \
    --disable-static \
    --disable-maintainer-mode
%make_build

%install
rm -rf %{buildroot}
%make_install

# Replace upstream's commented-out template with the Tenko defaults: Arc-Dark
# widgets, Kora icons and a black background.  Without an explicit icon theme
# the greeter falls back to hicolor, which lacks the symbolic indicator icons.
install -Dpm0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/lightdm/lightdm-gtk-greeter.conf

# Version the documentation directory.
mv -v %{buildroot}%{_docdir}/lightdm-gtk-greeter \
      %{buildroot}%{_docdir}/lightdm-gtk-greeter-%{version}

%files -f %{_sourcedir}/lightdm-gtk-greeter.filelist

%files lang -f %{_sourcedir}/lightdm-gtk-greeter-lang.filelist

%files doc -f %{_sourcedir}/lightdm-gtk-greeter-doc.filelist

%changelog
* Mon Nov 09 2026 tenko <build@tenko.invalid> 2.0.9-3
- Ship the Tenko greeter configuration: Arc-Dark GTK theme, Kora icons and
  a black background.  Without an icon theme the greeter fell back to
  hicolor, so the accessibility (and other symbolic) indicator icons were
  blank.  Require arc-theme and kora-icon-theme so the named themes resolve.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.0.9-2
- Build against lightdm instead of lightdm-devel: the -devel subpackages
  were removed and the .pc/GIR/headers now ship in lightdm (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.0.9-1
- Initial package (lightdm-gtk-greeter 2.0.9)
