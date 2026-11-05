Name:       at-spi2-core
Version:    2.62.1
Release:    5
Summary:    Assistive Technology Service Provider Interface core
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

Provides: pkgconfig(atspi-2)
%description
AT-SPI (Assistive Technology Service Provider Interface) is the core of an
accessibility stack for free software systems. It provides the D-Bus
interface definitions, the basic accessibility daemons, the ATK library
and the internal hooks between AT-SPI and ATK.

%package lang
Summary:    at-spi2-core translations
Requires:   at-spi2-core = %{version}-%{release}

%description lang
Translations for at-spi2-core.

%prep
%setup

%build
mkdir build
pushd build
meson setup ..                  \
      --prefix=/usr             \
      --buildtype=release       \
      -D gtk2_atk_adaptor=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%package gir
Summary:    GObject Introspection data for at-spi2-core
License:    LGPL-2.1-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for at-spi2-core, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/at-spi2-core.filelist
%files lang -f %{_sourcedir}/at-spi2-core-lang.filelist
%files gir -f %{_sourcedir}/at-spi2-core-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.62.1-5
- Replace the TODO summary/description and record the verified license
  (LGPL-2.1-or-later): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.62.1-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).
- Rebuild with the .pc Requires exclusion so atspi-2.pc does not pull
  dbus-daemon into a runtime install.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.62.1-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 0 paths updated.

* Mon Nov  2 2026 browneye <build@browneye.invalid> 2.62.1-1
- Update to 2.62.1 (current LFS/BLFS r13.1 trunk version).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.62.0.1-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.62.0.1-2
- Split lang, devel payload into at-spi2-core-lang, at-spi2-core-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.60.6
- Sync with BLFS r13.1 (2.48.3)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 3.30.1
- Initial RPM


