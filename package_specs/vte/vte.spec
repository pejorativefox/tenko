Name:       vte
Version:    0.84.1
Release:    4
Summary:    Virtual Terminal Emulator library
License:    LGPL-3.0-or-later
URL:        https://gitlab.gnome.org/GNOME/vte
Source0:    %{name}-%{version}.tar.gz
# Bundled subproject sources, matching vte-0.84.1's subprojects/*.wrap.
# Source1: simdutf v8.2.0
#   https://github.com/simdutf/simdutf/archive/refs/tags/v8.2.0.tar.gz
#   sha256 033a91b1d7d1cb818c1eff49e61faaa1b64a3a530d59ef9efef0195e56bda8b1
# Source2: fmt 12.1.0
#   https://github.com/fmtlib/fmt/archive/refs/tags/12.1.0.tar.gz
#   sha256 ea7de4299689e12b6dddd392f9896f08fb0777ac7168897a244a6d6085043fea
# Source3: fast_float v8.1.0
#   https://github.com/fastfloat/fast_float/archive/refs/tags/v8.1.0.tar.gz
#   sha256 4bfabb5979716995090ce68dce83f88f99629bc17ae280eae79311c5340143e1
Source1:    simdutf-8.2.0.tar.gz
Source2:    fmt-12.1.0.tar.gz
Source3:    fast_float-8.1.0.tar.gz
Prefix:     /usr

BuildRequires: gtk+
BuildRequires: gnutls
BuildRequires: libxml2
BuildRequires: fribidi
BuildRequires: pcre2
BuildRequires: lz4
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: pango

%description
Virtual Terminal Emulator library.

%prep
%setup -q

# Populate the subprojects from the bundled tarballs (the wraps point at
# GitHub, so the build must not try to fetch them at configure time).
mkdir -p subprojects/simdutf subprojects/fmt subprojects/fast_float
tar -xf %{SOURCE1} -C subprojects/simdutf --strip-components=1
tar -xf %{SOURCE2} -C subprojects/fmt --strip-components=1
tar -xf %{SOURCE3} -C subprojects/fast_float --strip-components=1

# VTE ships meson build files for these subprojects; overlay them so each
# extracted upstream source tree is buildable by Meson.
cp -f subprojects/packagefiles/simdutf/meson.build   subprojects/simdutf/meson.build
cp -f subprojects/packagefiles/simdutf/meson.options subprojects/simdutf/meson.options
cp -f subprojects/packagefiles/fmt/meson.build       subprojects/fmt/meson.build
cp -f subprojects/packagefiles/fast_float/meson.build subprojects/fast_float/meson.build

%build
mkdir build
pushd build
meson setup ..                  \
      --prefix=/usr             \
      --libdir=%{_libdir}       \
      --buildtype=release       \
      -Dgtk4=false              \
      -Dgtk3=true               \
      -Dgnutls=true             \
      -Dicu=false               \
      -Dvapi=false              \
      -Dgir=false               \
      -Ddocs=false              \
      -Dapp=false               \
      -Dglade=false             \
      -D_systemd=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -f %{buildroot}/etc/profile.d/vte.*
rmdir %{buildroot}/etc/profile.d 2>/dev/null || true
rmdir %{buildroot}/etc 2>/dev/null || true

%files -f %{_sourcedir}/vte.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.84.1-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.84.1-3
- Split devel payload into vte-devel (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.84.1-2
- Rebuild with GnuTLS 3.8.13 enabled (-Dgnutls=true) so VTE no longer
  warns that data will be written to disk unencrypted

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.84.1
- Update to VTE 0.84.1
- Build GTK3/X11 only; bundle simdutf 8.2.0, fmt 12.1.0 and
  fast_float 8.1.0 from VTE's subproject wraps for offline builds

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.59.0
- Added this sample to help with adding new packages.
