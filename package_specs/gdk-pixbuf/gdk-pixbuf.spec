Name:       gdk-pixbuf
Version:    2.44.8
Release:    2
Summary:    Image loading library
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
GdkPixbuf is a library that loads image data in various formats and stores it as linear buffers in memory.

%package lang
Summary:    gdk-pixbuf translations
Requires:   gdk-pixbuf = %{version}-%{release}

%description lang
Translations for gdk-pixbuf.

%package tests
Summary:    gdk-pixbuf tests
Requires:   gdk-pixbuf = %{version}-%{release}

%description tests
Test suite and test data for gdk-pixbuf.

%package devel
Summary:    gdk-pixbuf development files
Requires:   gdk-pixbuf = %{version}-%{release}
Provides: pkgconfig(gdk-pixbuf-2.0)

%description devel
Development files for gdk-pixbuf.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                \
      --prefix=/usr           \
      --buildtype=release     \
      -D png=enabled          \
      -D gif=disabled         \
      -D jpeg=enabled        \
      -D tiff=disabled        \
      -D thumbnailer=disabled \
      -D glycin=disabled      \
      -D man=false           \
      --wrap-mode=nofallback
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/gdk-pixbuf.filelist
%files lang -f %{_sourcedir}/gdk-pixbuf-lang.filelist
%files tests -f %{_sourcedir}/gdk-pixbuf-tests.filelist
%files devel -f %{_sourcedir}/gdk-pixbuf-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.44.8-2
- Split lang, tests, devel payload into gdk-pixbuf-lang, gdk-pixbuf-tests, gdk-pixbuf-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.44.7
- Sync with BLFS r13.1 (2.42.9)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 2.42.9
- Version bump
