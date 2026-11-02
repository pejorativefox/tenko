Name:       at-spi2-core
Version:    2.62.1
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
TODO

%package lang
Summary:    at-spi2-core translations
Requires:   at-spi2-core = %{version}-%{release}

%description lang
Translations for at-spi2-core.

%package devel
Summary:    at-spi2-core development files
Requires:   %{name}-gir = %{version}-%{release}
Requires:   at-spi2-core = %{version}-%{release}
Provides: pkgconfig(atspi-2)

%description devel
Development files for at-spi2-core.

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
License:    GPL3
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for at-spi2-core, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the -devel package.

%files -f %{_sourcedir}/at-spi2-core.filelist
%files lang -f %{_sourcedir}/at-spi2-core-lang.filelist
%files devel -f %{_sourcedir}/at-spi2-core-devel.filelist
%files gir -f %{_sourcedir}/at-spi2-core-gir.filelist


%changelog
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


