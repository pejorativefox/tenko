Name:       gobject-introspection
Version:    1.86.0
Release:    7
Summary:    GObject API introspection tools and library
License:    GPL-2.0-or-later AND LGPL-2.0-or-later AND MIT
URL:        https://gi.readthedocs.io/en/latest/
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
Requires: python-setuptools
BuildRequires: python-setuptools

%description
GObject Introspection describes the APIs of GObject-based libraries and
collects them in a uniform, machine-readable GIR format. It provides the
typelib library and tools such as g-ir-scanner, g-ir-compiler and
g-ir-generate.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%package gir
Summary:    GObject Introspection data for gobject-introspection
License:    GPL-2.0-or-later AND LGPL-2.0-or-later AND MIT
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for gobject-introspection.  g-ir-scanner works
without this package (it reads the .gir XML); g-ir-inspect and
language bindings need it.

%files -f %{_sourcedir}/gobject-introspection.filelist
%files gir -f %{_sourcedir}/gobject-introspection-gir.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 1.86.0-7
- Require python-setuptools: g-ir-scanner imports distutils, which only setuptools provides on Python 3.12+.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.86.0-6
- Replace the TODO summary/description and record the verified license
  (GPL-2.0-or-later AND LGPL-2.0-or-later AND MIT): COPYING (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.86.0-5
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.86.0-3
- Rebuild for Python 3.15: g-ir-scanner's _giscanner extension was
  built for 3.14, which breaks every introspection build on 3.15.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.86.0-2
- Split the GObject Introspection typelibs into %{name}-gir
# let's skip this for now

