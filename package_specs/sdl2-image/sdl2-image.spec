Name:       sdl2-image
Version:    2.8.12
Release:    1
Summary:    SDL_image is an image file loading library
License:    zlib
Source0:    SDL2_image-%{version}.tar.gz
Prefix:     /usr

BuildRequires: sdl2
BuildRequires: libpng
BuildRequires: libjpeg-turbo
BuildRequires: webp

# The codec libraries are loaded with dlopen() at runtime, so rpm cannot
# discover them from the ELF headers.
Requires: libpng
Requires: libjpeg-turbo
Requires: webp

%description
SDL_image is an image file loading library that supports BMP, GIF,
JPEG, LBM, PCX, PNG, PNM, SVG, TGA, WEBP, XCF, XPM and XV images.

%prep
%setup -q -n SDL2_image-%{version}

%build
%configure \
    --disable-static \
    --disable-stb-image \
    --disable-tif \
    --disable-avif \
    --disable-jxl
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/sdl2-image.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.8.12-1
- Not in the r13.1 book; latest SDL2-series upstream release
  (2026-11-05).
- Build shared only against the published SDL2 2.32.74, libpng
  1.6.59, libjpeg-turbo 3.2.1 and webp 1.6.0.
- Disable libtiff, libavif and libjxl support (not in the distro) and
  the bundled stb_image backend, so the system libraries are used.
- Refresh %files from the build (no -devel split).
- Require libpng, libjpeg-turbo and webp at runtime, because SDL_image
  loads those codecs with dlopen().
