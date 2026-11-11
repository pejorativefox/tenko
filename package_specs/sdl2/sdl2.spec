Name:       sdl2 
Version:    2.32.74
Release:    1
Summary:    Simple Direct Media Layer 2
License:    GPM
Source0:    sdl2-compat-%{version}.tar.gz
Prefix:     /usr

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
* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.32.74-1
- Track upstream: sdl2 is now sdl2-compat (a shim over sdl3)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 2.0.8
- Initial RPM

