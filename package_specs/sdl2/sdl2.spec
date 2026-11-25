Name:       sdl2 
Version:    2.32.74
Release:    2
Summary:    Simple Direct Media Layer 2
License:    GPM
URL:        https://github.com/libsdl-org/sdl2-compat
Source0:    sdl2-compat-%{version}.tar.gz
Prefix:     /usr
BuildRequires: sdl3
BuildRequires: libx11
BuildRequires: libXdmcp
BuildRequires: libxau
BuildRequires: libxcb
BuildRequires: xorgproto

# sdl2-compat dlopens libSDL3.so.0 at runtime; without sdl3 installed
# every program that links libSDL2 aborts with "Failed loading SDL3
# library." (seen with gegl's sdl2-display operation inside GIMP).
Requires:   sdl3

%description
Simple DirectMedia Layer is a cross-platform development library designed to 
provide low level access to audio, keyboard, mouse, joystick, and graphics 
hardware via OpenGL and Direct3D.

%prep
%setup -q -n sdl2-compat-%{version}

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr      \
      -D CMAKE_BUILD_TYPE=Release       \
      -D CMAKE_INSTALL_LIBDIR=lib64     \
      -D CMAKE_SKIP_INSTALL_RPATH=ON    \
      -D SDL2COMPAT_STATIC=OFF          \
      -D SDL2COMPAT_TESTS=OFF           \
      -W no-author ..
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
make DESTDIR=%{buildroot} install
popd

%files -f %{_sourcedir}/sdl2.filelist

%changelog
* Wed Nov 25 2026 tenko <build@tenko.invalid> 2.32.74-2
- Require sdl3 at runtime: sdl2-compat dlopens libSDL3.so.0, and
  programs linking libSDL2 abort when it is missing.  Found while
  building gimp (gegl's sdl2-display operation aborted every
  gimp-console start, so the splash image generation failed).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.32.74-1
- Track upstream: sdl2 is now sdl2-compat (a shim over sdl3)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 2.0.8
- Initial RPM

