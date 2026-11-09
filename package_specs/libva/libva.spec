Name:       libva
Version:    2.24.1
Release:    1
Summary:    Video Acceleration API (VA-API) library
License:    MIT
URL:        https://github.com/intel/libva
Source0:    libva-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: gcc
BuildRequires: libdrm
BuildRequires: libx11
BuildRequires: libxcb
BuildRequires: libxext
BuildRequires: libxfixes
BuildRequires: mesa
BuildRequires: meson
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: xorgproto

%description
libva is the reference implementation of the Video Acceleration API
(VA-API), the vendor-neutral interface that applications use to offload
video decode, encode and processing to the GPU.  This package provides the
core runtime library together with the DRM and X11 backends used on the
Tenko X11/XFCE desktop, including the headers and pkg-config files needed
to build against it.  The Wayland backend is not built.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release \
    -Dwith_x11=yes       \
    -Dwith_glx=yes       \
    -Dwith_wayland=no    \
    -Denable_docs=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libva.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 2.24.1-1
- Initial package, tracking the latest stable upstream release (2.24.1).
- The licence was verified as MIT from the upstream COPYING file.
- Build the DRM, X11 and GLX backends.  The Wayland backend is disabled
  because Tenko is an X11/XFCE distribution.
