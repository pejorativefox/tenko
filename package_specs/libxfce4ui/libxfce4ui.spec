Name:       libxfce4ui
Version:    4.20.2
Release:    5
Summary:    Commonly used Xfce widgets among Xfce applications
License:    GPL-2.0-or-later AND LGPL-2.0-or-later
URL:        https://docs.xfce.org/xfce/libxfce4ui/start
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: xfconf
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: harfbuzz
BuildRequires: libice
BuildRequires: libsm
BuildRequires: libx11
BuildRequires: libxfce4util
BuildRequires: pango
BuildRequires: startup-notification

%description
Commonly used Xfce widgets among Xfce applications

%package lang
Summary:    libxfce4ui translations
Requires:   libxfce4ui = %{version}-%{release}

%description lang
Translations for libxfce4ui.

%package doc
Summary:    libxfce4ui documentation
Requires:   libxfce4ui = %{version}-%{release}

%description doc
Documentation for libxfce4ui.

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
Summary:    GObject Introspection data for libxfce4ui
License:    GPL-2.0-or-later AND LGPL-2.0-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for libxfce4ui, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/libxfce4ui.filelist
%files lang -f %{_sourcedir}/libxfce4ui-lang.filelist
%files doc -f %{_sourcedir}/libxfce4ui-doc.filelist
%files gir -f %{_sourcedir}/libxfce4ui-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.2-5
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND LGPL-2.0-or-later): COPYING, GNU Library GPL v2, plus libxfce4ui/*.c and xfce4-about/main.c (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.2-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20.2-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.2-2
- Split lang, doc, devel payload into libxfce4ui-lang, libxfce4ui-doc, libxfce4ui-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.2
- Sync with 4.19.2

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.2
- Version Bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.1
- Initial RPM

