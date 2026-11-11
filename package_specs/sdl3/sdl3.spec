Name:       sdl3
Version:    3.4.18
Release:    1
Summary:    Simple DirectMedia Layer 3, a cross-platform multimedia library
License:    Zlib
URL:        https://www.libsdl.org/
Source0:    SDL3-%{version}.tar.gz
Patch0:     SDL3-%{version}-upstream_fixes-1.patch
Prefix:     /usr
BuildRequires: alsa-lib
BuildRequires: fribidi
BuildRequires: libdrm
BuildRequires: libusb
BuildRequires: libx11
BuildRequires: libxkbcommon
BuildRequires: mesa
BuildRequires: pipewire
BuildRequires: pulseaudio
BuildRequires: wayland

%description
Simple DirectMedia Layer is a cross-platform development library
designed to provide low level access to audio, keyboard, mouse,
joystick, and graphics hardware via OpenGL and Vulkan.

%prep
%setup -q -n SDL3-%{version}
%patch -P 0 -p1

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_BUILD_TYPE=Release  \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D SDL_TEST_LIBRARY=OFF      \
      -D SDL_STATIC=OFF            \
      -D SDL_RPATH=OFF             \
      -W no-author -G Ninja ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/sdl3.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.4.18-1
- New package, required by sdl2-compat
