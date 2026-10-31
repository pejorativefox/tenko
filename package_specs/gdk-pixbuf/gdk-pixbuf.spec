Name:       gdk-pixbuf
Version:    2.44.7
Release:    1
Summary:    Image loading library
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
Provides: pkgconfig(gdk-pixbuf-2.0)

%description
GdkPixbuf is a library that loads image data in various formats and stores it as linear buffers in memory.

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


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.44.7
- Sync with BLFS r13.1 (2.42.9)

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 2.42.9
- Version bump
