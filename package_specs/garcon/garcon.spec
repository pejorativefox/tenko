Name:       garcon
Version:    4.20.0
Release:    5
Summary:    Implementation of the freedesktop.org menu specification
License:    LGPL-2.0-or-later
URL:        https://docs.xfce.org/xfce/garcon/start
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: libxfce4ui
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: harfbuzz
BuildRequires: libxfce4util
BuildRequires: pango
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
BuildRequires: xfconf
BuildRequires: xorgproto
BuildRequires: gobject-introspection

%description
Implementation of the freedesktop.org menu specification

%package doc
Summary:    garcon documentation
License:    GFDL-1.1-no-invariants-only
Requires:   garcon = %{version}-%{release}

%description doc
Documentation for garcon.

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%package gir
Summary:    GObject Introspection data for garcon
License:    LGPL-2.0-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for garcon, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/garcon.filelist
%files doc -f %{_sourcedir}/garcon-doc.filelist
%files gir -f %{_sourcedir}/garcon-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.0-5
- Replace the legacy short licence name with the verified SPDX expressions
  (LGPL-2.0-or-later for the code and GIR, GFDL-1.1-no-invariants-only for the docs):
  COPYING and the garcon/ headers (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.0-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20.0-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.0-2
- Split doc, devel payload into garcon-doc, garcon-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.0
- Sync with 4.19.0

* Wed Aug 30 2023  Chris Statzer <chris.statzer@gmail.com> 4.19.0

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.6.4
- Initial RPM

