Name:       libxfce4util
Version:    4.20.1
Release:    5
Summary:    Basic utility library for Xfce4.
License:    GPL-2.0-or-later AND LGPL-2.0-or-later
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
Basic utility library for Xfce4.

%package lang
Summary:    libxfce4util translations
Requires:   libxfce4util = %{version}-%{release}

%description lang
Translations for libxfce4util.

%package doc
Summary:    libxfce4util documentation
Requires:   libxfce4util = %{version}-%{release}

%description doc
Documentation for libxfce4util.

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
Summary:    GObject Introspection data for libxfce4util
License:    GPL-2.0-or-later AND LGPL-2.0-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for libxfce4util, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/libxfce4util.filelist
%files lang -f %{_sourcedir}/libxfce4util-lang.filelist
%files doc -f %{_sourcedir}/libxfce4util-doc.filelist
%files gir -f %{_sourcedir}/libxfce4util-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.1-5
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND LGPL-2.0-or-later): COPYING, GNU Library GPL v2, plus libxfce4util/*.c and xfce4-kiosk-query/main.c (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.1-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20.1-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.1-2
- Split lang, doc, devel payload into libxfce4util-lang, libxfce4util-doc, libxfce4util-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.1
- Sync with 4.19.2

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.2
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

