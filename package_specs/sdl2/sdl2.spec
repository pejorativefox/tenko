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

%files
/usr/bin/sdl2-config
/usr/include/SDL2/SDL.h
/usr/include/SDL2/SDL_assert.h
/usr/include/SDL2/SDL_atomic.h
/usr/include/SDL2/SDL_audio.h
/usr/include/SDL2/SDL_bits.h
/usr/include/SDL2/SDL_blendmode.h
/usr/include/SDL2/SDL_clipboard.h
/usr/include/SDL2/SDL_config.h
/usr/include/SDL2/SDL_config_android.h
/usr/include/SDL2/SDL_config_emscripten.h
/usr/include/SDL2/SDL_config_iphoneos.h
/usr/include/SDL2/SDL_config_macosx.h
/usr/include/SDL2/SDL_config_minimal.h
/usr/include/SDL2/SDL_config_ngage.h
/usr/include/SDL2/SDL_config_os2.h
/usr/include/SDL2/SDL_config_pandora.h
/usr/include/SDL2/SDL_config_unix.h
/usr/include/SDL2/SDL_config_windows.h
/usr/include/SDL2/SDL_config_wingdk.h
/usr/include/SDL2/SDL_config_winrt.h
/usr/include/SDL2/SDL_config_xbox.h
/usr/include/SDL2/SDL_copying.h
/usr/include/SDL2/SDL_cpuinfo.h
/usr/include/SDL2/SDL_egl.h
/usr/include/SDL2/SDL_endian.h
/usr/include/SDL2/SDL_error.h
/usr/include/SDL2/SDL_events.h
/usr/include/SDL2/SDL_filesystem.h
/usr/include/SDL2/SDL_gamecontroller.h
/usr/include/SDL2/SDL_gesture.h
/usr/include/SDL2/SDL_guid.h
/usr/include/SDL2/SDL_haptic.h
/usr/include/SDL2/SDL_hidapi.h
/usr/include/SDL2/SDL_hints.h
/usr/include/SDL2/SDL_joystick.h
/usr/include/SDL2/SDL_keyboard.h
/usr/include/SDL2/SDL_keycode.h
/usr/include/SDL2/SDL_loadso.h
/usr/include/SDL2/SDL_locale.h
/usr/include/SDL2/SDL_log.h
/usr/include/SDL2/SDL_main.h
/usr/include/SDL2/SDL_messagebox.h
/usr/include/SDL2/SDL_metal.h
/usr/include/SDL2/SDL_misc.h
/usr/include/SDL2/SDL_mouse.h
/usr/include/SDL2/SDL_mutex.h
/usr/include/SDL2/SDL_name.h
/usr/include/SDL2/SDL_opengl.h
/usr/include/SDL2/SDL_opengl_glext.h
/usr/include/SDL2/SDL_opengles.h
/usr/include/SDL2/SDL_opengles2.h
/usr/include/SDL2/SDL_opengles2_gl2.h
/usr/include/SDL2/SDL_opengles2_gl2ext.h
/usr/include/SDL2/SDL_opengles2_gl2platform.h
/usr/include/SDL2/SDL_opengles2_khrplatform.h
/usr/include/SDL2/SDL_pixels.h
/usr/include/SDL2/SDL_platform.h
/usr/include/SDL2/SDL_power.h
/usr/include/SDL2/SDL_quit.h
/usr/include/SDL2/SDL_rect.h
/usr/include/SDL2/SDL_render.h
/usr/include/SDL2/SDL_revision.h
/usr/include/SDL2/SDL_rwops.h
/usr/include/SDL2/SDL_scancode.h
/usr/include/SDL2/SDL_sensor.h
/usr/include/SDL2/SDL_shape.h
/usr/include/SDL2/SDL_stdinc.h
/usr/include/SDL2/SDL_surface.h
/usr/include/SDL2/SDL_system.h
/usr/include/SDL2/SDL_syswm.h
/usr/include/SDL2/SDL_test.h
/usr/include/SDL2/SDL_test_assert.h
/usr/include/SDL2/SDL_test_common.h
/usr/include/SDL2/SDL_test_compare.h
/usr/include/SDL2/SDL_test_crc32.h
/usr/include/SDL2/SDL_test_font.h
/usr/include/SDL2/SDL_test_fuzzer.h
/usr/include/SDL2/SDL_test_harness.h
/usr/include/SDL2/SDL_test_images.h
/usr/include/SDL2/SDL_test_log.h
/usr/include/SDL2/SDL_test_md5.h
/usr/include/SDL2/SDL_test_memory.h
/usr/include/SDL2/SDL_test_random.h
/usr/include/SDL2/SDL_thread.h
/usr/include/SDL2/SDL_timer.h
/usr/include/SDL2/SDL_touch.h
/usr/include/SDL2/SDL_types.h
/usr/include/SDL2/SDL_version.h
/usr/include/SDL2/SDL_video.h
/usr/include/SDL2/SDL_vulkan.h
/usr/include/SDL2/begin_code.h
/usr/include/SDL2/close_code.h
/usr/lib64/cmake/SDL2/SDL2Config.cmake
/usr/lib64/cmake/SDL2/SDL2ConfigVersion.cmake
/usr/lib64/cmake/SDL2/SDL2Targets-release.cmake
/usr/lib64/cmake/SDL2/SDL2Targets.cmake
/usr/lib64/cmake/SDL2/SDL2_testTargets-release.cmake
/usr/lib64/cmake/SDL2/SDL2_testTargets.cmake
/usr/lib64/cmake/SDL2/SDL2mainTargets-release.cmake
/usr/lib64/cmake/SDL2/SDL2mainTargets.cmake
/usr/lib64/cmake/SDL2/sdl2-config-version.cmake
/usr/lib64/cmake/SDL2/sdl2-config.cmake
/usr/lib64/libSDL2-2.0.so
/usr/lib64/libSDL2-2.0.so.0
/usr/lib64/libSDL2-2.0.so.0.3200.74
/usr/lib64/libSDL2.so
/usr/lib64/libSDL2_test.a
/usr/lib64/libSDL2main.a
/usr/lib64/pkgconfig/sdl2-compat.pc
/usr/share/aclocal/sdl2.m4
/usr/share/licenses/sdl2-compat/LICENSE.txt

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.32.74-1
- Track upstream: sdl2 is now sdl2-compat (a shim over sdl3)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 2.0.8
- Initial RPM

