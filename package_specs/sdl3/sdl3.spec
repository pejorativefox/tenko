Name:       sdl3
Version:    3.4.18
Release:    1
Summary:    Simple DirectMedia Layer 3, a cross-platform multimedia library
License:    Zlib
Source0:    SDL3-%{version}.tar.gz
Source1:    SDL3-%{version}-upstream_fixes-1.patch
Prefix:     /usr

%description
Simple DirectMedia Layer is a cross-platform development library
designed to provide low level access to audio, keyboard, mouse,
joystick, and graphics hardware via OpenGL and Vulkan.

%prep
%setup -q -n SDL3-%{version}
patch -Np1 -i %{SOURCE1}

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

%files
/usr/include/SDL3/SDL.h
/usr/include/SDL3/SDL_assert.h
/usr/include/SDL3/SDL_asyncio.h
/usr/include/SDL3/SDL_atomic.h
/usr/include/SDL3/SDL_audio.h
/usr/include/SDL3/SDL_begin_code.h
/usr/include/SDL3/SDL_bits.h
/usr/include/SDL3/SDL_blendmode.h
/usr/include/SDL3/SDL_camera.h
/usr/include/SDL3/SDL_clipboard.h
/usr/include/SDL3/SDL_close_code.h
/usr/include/SDL3/SDL_copying.h
/usr/include/SDL3/SDL_cpuinfo.h
/usr/include/SDL3/SDL_dialog.h
/usr/include/SDL3/SDL_dlopennote.h
/usr/include/SDL3/SDL_egl.h
/usr/include/SDL3/SDL_endian.h
/usr/include/SDL3/SDL_error.h
/usr/include/SDL3/SDL_events.h
/usr/include/SDL3/SDL_filesystem.h
/usr/include/SDL3/SDL_gamepad.h
/usr/include/SDL3/SDL_gpu.h
/usr/include/SDL3/SDL_guid.h
/usr/include/SDL3/SDL_haptic.h
/usr/include/SDL3/SDL_hidapi.h
/usr/include/SDL3/SDL_hints.h
/usr/include/SDL3/SDL_init.h
/usr/include/SDL3/SDL_intrin.h
/usr/include/SDL3/SDL_iostream.h
/usr/include/SDL3/SDL_joystick.h
/usr/include/SDL3/SDL_keyboard.h
/usr/include/SDL3/SDL_keycode.h
/usr/include/SDL3/SDL_loadso.h
/usr/include/SDL3/SDL_locale.h
/usr/include/SDL3/SDL_log.h
/usr/include/SDL3/SDL_main.h
/usr/include/SDL3/SDL_main_impl.h
/usr/include/SDL3/SDL_messagebox.h
/usr/include/SDL3/SDL_metal.h
/usr/include/SDL3/SDL_misc.h
/usr/include/SDL3/SDL_mouse.h
/usr/include/SDL3/SDL_mutex.h
/usr/include/SDL3/SDL_oldnames.h
/usr/include/SDL3/SDL_opengl.h
/usr/include/SDL3/SDL_opengl_glext.h
/usr/include/SDL3/SDL_opengles.h
/usr/include/SDL3/SDL_opengles2.h
/usr/include/SDL3/SDL_opengles2_gl2.h
/usr/include/SDL3/SDL_opengles2_gl2ext.h
/usr/include/SDL3/SDL_opengles2_gl2platform.h
/usr/include/SDL3/SDL_opengles2_khrplatform.h
/usr/include/SDL3/SDL_pen.h
/usr/include/SDL3/SDL_pixels.h
/usr/include/SDL3/SDL_platform.h
/usr/include/SDL3/SDL_platform_defines.h
/usr/include/SDL3/SDL_power.h
/usr/include/SDL3/SDL_process.h
/usr/include/SDL3/SDL_properties.h
/usr/include/SDL3/SDL_rect.h
/usr/include/SDL3/SDL_render.h
/usr/include/SDL3/SDL_revision.h
/usr/include/SDL3/SDL_scancode.h
/usr/include/SDL3/SDL_sensor.h
/usr/include/SDL3/SDL_stdinc.h
/usr/include/SDL3/SDL_storage.h
/usr/include/SDL3/SDL_surface.h
/usr/include/SDL3/SDL_system.h
/usr/include/SDL3/SDL_thread.h
/usr/include/SDL3/SDL_time.h
/usr/include/SDL3/SDL_timer.h
/usr/include/SDL3/SDL_touch.h
/usr/include/SDL3/SDL_tray.h
/usr/include/SDL3/SDL_version.h
/usr/include/SDL3/SDL_video.h
/usr/include/SDL3/SDL_vulkan.h
/usr/lib64/cmake/SDL3/SDL3Config.cmake
/usr/lib64/cmake/SDL3/SDL3ConfigVersion.cmake
/usr/lib64/cmake/SDL3/SDL3headersTargets.cmake
/usr/lib64/cmake/SDL3/SDL3sharedTargets-release.cmake
/usr/lib64/cmake/SDL3/SDL3sharedTargets.cmake
/usr/lib64/libSDL3.so
/usr/lib64/libSDL3.so.0
/usr/lib64/libSDL3.so.0.4.18
/usr/lib64/pkgconfig/sdl3.pc
/usr/share/licenses/SDL3/LICENSE.txt

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.4.18-1
- New package: BLFS r13.1 build, required by sdl2-compat
