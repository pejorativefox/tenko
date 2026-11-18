Name:       sdl3-ttf
Version:    3.2.2
Release:    1
Summary:    SDL3_ttf is a TrueType font rendering library
License:    Zlib
URL:        https://github.com/libsdl-org/SDL_ttf
Source0:    SDL3_ttf-%{version}.tar.gz
Prefix:     /usr

BuildRequires: sdl3
BuildRequires: freetype
BuildRequires: harfbuzz

%description
SDL3_ttf is a TrueType font rendering library that supports text
shaping through HarfBuzz.

%prep
%setup -q -n SDL3_ttf-%{version}

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D CMAKE_BUILD_TYPE=Release \
      -D SDLTTF_PLUTOSVG=OFF \
      -D SDLTTF_STRICT=ON \
      -W no-author -G Ninja ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/sdl3-ttf.filelist

%changelog
* Wed Nov 18 2026 browneye <build@browneye.invalid> 3.2.2-1
- New package, not in the base set: latest upstream stable release
  (3.2.2, checked 2026-11-18).
- Link freetype and harfbuzz directly; disable plutosvg color-emoji
  support (not in the distro).
