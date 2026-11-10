Name:       ristretto
Version:    0.14.0
Release:    1
Summary:    Image viewer for Xfce
License:    GPL-2.0-or-later
URL:        https://docs.xfce.org/apps/ristretto/start
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: gtk+
BuildRequires: cairo
BuildRequires: libexif
BuildRequires: libxfce4ui
BuildRequires: libxfce4util
BuildRequires: xfconf
BuildRequires: exo
BuildRequires: libx11
BuildRequires: file
BuildRequires: gettext
BuildRequires: meson
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: gcc
Requires:   libexif
Requires:   libxfce4ui
Requires:   libxfce4util
Requires:   xfconf
Requires:   exo

%description
Ristretto is a fast, lightweight image viewer for the Xfce desktop.  It
browses and displays images, supports zooming, full-screen and slideshow
viewing, and can set the desktop wallpaper.

%package lang
Summary:    ristretto translations
Requires:   ristretto = %{version}-%{release}

%description lang
Translations for ristretto.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -Dlibx11=enabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/ristretto.filelist
%files lang -f %{_sourcedir}/ristretto-lang.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 0.14.0-1
- Initial package.  Ristretto is not in the base set.
- Version 0.14.0 is the latest stable upstream release (2026-03-08).
- Source: https://archive.xfce.org/src/apps/ristretto/0.14/ristretto-0.14.0.tar.xz
  md5 63b94c3e3fab28c4533697f36ee6caa2
  sha256 502cf1577de14b38132dc89e56884c5e10f86f6a028d8dde379a8839110fda55
- Build with libX11 support and the libexif metadata reader; libmagic is
  used when the file package's magic.h is present in the build image.
