Name:       thunar
Version:    4.20.10
Release:    6
Summary:    Modern file manager for Xfce
License:    GPL-2.0-or-later AND LGPL-2.0-or-later
URL:        https://docs.xfce.org/xfce/thunar/start
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

Requires:   gvfs
Requires:   gvfs-smb
Requires:   gvfs-fuse
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: exo
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: harfbuzz
BuildRequires: libgudev
BuildRequires: libice
BuildRequires: libnotify
BuildRequires: libsm
BuildRequires: libx11
BuildRequires: libxfce4ui
BuildRequires: libxfce4util
BuildRequires: pango
BuildRequires: xfce4-panel
BuildRequires: xfconf
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
BuildRequires: shared-mime-info
BuildRequires: xorgproto
BuildRequires: gobject-introspection

%description
Modern file manager for Xfce

%package lang
Summary:    thunar translations
Requires:   thunar = %{version}-%{release}

%description lang
Translations for thunar.

%package doc
Summary:    thunar documentation
Requires:   thunar = %{version}-%{release}

%description doc
Documentation for thunar.

%prep
%setup 

%build
sed -i 's/\tinstall-systemd_userDATA/\t/' Makefile.in
%configure --docdir=/usr/share/doc/thunar-%{version}
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%package gir
Summary:    GObject Introspection data for thunar
License:    GPL-2.0-or-later AND LGPL-2.0-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for thunar, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/thunar.filelist
%files lang -f %{_sourcedir}/thunar-lang.filelist
%files doc -f %{_sourcedir}/thunar-doc.filelist
%files gir -f %{_sourcedir}/thunar-gir.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 4.20.10-6
- Hard-require gvfs, gvfs-smb and gvfs-fuse so SMB shares can be browsed
  in Thunar out of the box.  The SMB and FUSE backends are part of the
  supported desktop experience, not an optional add-on.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.10-5
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND LGPL-2.0-or-later): COPYING, COPYING.LIB (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.10-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20.10-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.10-2
- Split lang, doc, devel payload into thunar-lang, thunar-doc, thunar-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.9
- Sync with 4.18.6

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.18.6
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.8.9
- Initial RPM

