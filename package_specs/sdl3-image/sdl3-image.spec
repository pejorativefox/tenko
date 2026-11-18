Name:       sdl3-image
Version:    3.4.8
Release:    1
Summary:    SDL3_image is an image file loading library
License:    Zlib
URL:        https://github.com/libsdl-org/SDL_image
Source0:    SDL3_image-%{version}.tar.gz
Prefix:     /usr

BuildRequires: sdl3
BuildRequires: libpng
BuildRequires: libjpeg-turbo
BuildRequires: webp

# libtiff, libavif and libjxl are not in the distro; those formats are
# disabled explicitly so the strict dependency check does not see them.
%description
SDL3_image is an image file loading library that supports BMP, GIF,
JPEG, LBM, PCX, PNG, PNM, QOI, SVG, TGA, WEBP, XCF, XPM and XV images.

%prep
%setup -q -n SDL3_image-%{version}

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D CMAKE_BUILD_TYPE=Release \
      -D SDLIMAGE_DEPS_SHARED=OFF \
      -D SDLIMAGE_BACKEND_STB=OFF \
      -D SDLIMAGE_TIF=OFF \
      -D SDLIMAGE_AVIF=OFF \
      -D SDLIMAGE_JXL=OFF \
      -D SDLIMAGE_STRICT=ON \
      -W no-author -G Ninja ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/sdl3-image.filelist

%changelog
* Wed Nov 18 2026 browneye <build@browneye.invalid> 3.4.8-1
- New package, not in the base set: latest upstream stable release
  (3.4.8, checked 2026-11-18).
- Link libpng, libjpeg-turbo and webp directly (SDLIMAGE_DEPS_SHARED=OFF)
  so rpm tracks the codec dependencies; SVG and QOI use the bundled
  decoders.  The bundled stb_image JPEG backend is off so JPEG goes
  through system libjpeg-turbo.
- Disable libtiff, libavif and libjxl support (not in the distro).
