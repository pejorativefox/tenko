Name:       xfce4-panel
Version:    4.20.8
Release:    5
Summary:    Panel for the Xfce desktop environment
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
URL:        https://docs.xfce.org/xfce/xfce4-panel/start
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: libxfce4util
BuildRequires: garcon
BuildRequires: exo
BuildRequires: libxfce4windowing

%description
Panel for the Xfce desktop environment

%package lang
Summary:    xfce4-panel translations
Requires:   xfce4-panel = %{version}-%{release}

%description lang
Translations for xfce4-panel.

%package doc
Summary:    xfce4-panel documentation
Requires:   xfce4-panel = %{version}-%{release}

%description doc
Documentation for xfce4-panel.

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
Summary:    GObject Introspection data for xfce4-panel
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for xfce4-panel, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/xfce4-panel.filelist
%files lang -f %{_sourcedir}/xfce4-panel-lang.filelist
%files doc -f %{_sourcedir}/xfce4-panel-doc.filelist
%files gir -f %{_sourcedir}/xfce4-panel-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.8-5
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND LGPL-2.1-or-later): COPYING, COPYING.LIB (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.8-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20.8-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.8-2
- Split lang, doc, devel payload into xfce4-panel-lang, xfce4-panel-doc, xfce4-panel-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.8
- Sync with 4.19.1

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

