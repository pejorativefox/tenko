Name:       libva-utils
Version:    2.24.0
Release:    1
Summary:    Utilities and tests for the Video Acceleration API (VA-API)
License:    MIT
URL:        https://github.com/intel/libva-utils
Source0:    libva-utils-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: gcc
BuildRequires: libdrm
BuildRequires: libva
BuildRequires: libx11
BuildRequires: pkgconf

%description
libva-utils is a collection of utilities and example applications for
the Video Acceleration API (VA-API).  vainfo reports the profiles,
entry points and capabilities the installed drivers support, and the
decode, encode and video-processing samples exercise them.  Built
with the DRM and X11 backends; the Wayland backend is not built.

%prep
%setup -q

%build
%configure --enable-drm --enable-x11 --disable-wayland
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libva-utils.filelist

%changelog
* Fri Nov 20 2026 tenko <build@tenko.invalid> 2.24.0-1
- New package, not in the base set: latest upstream stable release
  (2.24.0, checked 2026-11-20), matching the libva 2.24.1 package.
- Build the DRM and X11 backends.  The Wayland backend is disabled
  because Tenko is an X11/XFCE distribution.
