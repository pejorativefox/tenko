Name:       mpv
Version:    0.42.0
Release:    1
Summary:    Media player for the command line
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
URL:        https://mpv.io/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: meson
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: ffmpeg
BuildRequires: libass
BuildRequires: libplacebo
BuildRequires: luajit
BuildRequires: mesa
BuildRequires: alsa-lib
BuildRequires: pulseaudio
BuildRequires: libjpeg-turbo
BuildRequires: libarchive
BuildRequires: curl
BuildRequires: libx11
BuildRequires: libxext
BuildRequires: libxinerama
BuildRequires: libxrandr
BuildRequires: libxscrnsaver
BuildRequires: libxv
BuildRequires: libxkbcommon
BuildRequires: libxcb
BuildRequires: python3-docutils

%description
mpv is a free media player for the command line.  It supports a wide
variety of media file formats, audio and video codecs, and subtitle types.

This build provides the mpv command-line player and libmpv with X11 video
output, OpenGL/EGL rendering through libplacebo, ALSA and PulseAudio output,
LuaJIT scripting, and JPEG, libarchive and libcurl support.

%prep
%setup -q

%build
# ffmpeg installs its pkg-config files in /usr/lib/pkgconfig, which is not in
# pkgconf's default search path on this 64-bit-only distribution.
export PKG_CONFIG_PATH=/usr/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}
mkdir build
pushd build
meson setup ..                            \
    --prefix=/usr                         \
    --libdir=/usr/lib64                   \
    --buildtype=release                   \
    -Dcplayer=true                        \
    -Dlibmpv=true                         \
    -Dgpl=true                            \
    -Dbuild-date=false                    \
    -Dlua=luajit                          \
    -Dx11=enabled                         \
    -Dxv=enabled                          \
    -Dgl=enabled                          \
    -Degl=enabled                         \
    -Ddrm=disabled                        \
    -Dalsa=enabled                        \
    -Dpulse=enabled                       \
    -Dpipewire=disabled                   \
    -Djpeg=enabled                        \
    -Dlibarchive=enabled                  \
    -Dlibcurl=enabled                     \
    -Dzlib=enabled                        \
    -Dmanpage-build=enabled               \
    -Dwayland=disabled                    \
    -Dvulkan=disabled                     \
    -Dshaderc=disabled                    \
    -Dspirv-cross=disabled                \
    -Dvaapi=disabled                      \
    -Dvdpau=disabled                      \
    -Dcuda-hwaccel=disabled               \
    -Dcuda-interop=disabled               \
    -Djavascript=disabled                 \
    -Dcdda=disabled                       \
    -Ddvdnav=disabled                     \
    -Ddvda=disabled                       \
    -Dlibbluray=disabled                  \
    -Duchardet=disabled                   \
    -Dsubrandr=disabled                   \
    -Dlcms2=disabled                      \
    -Dzimg=disabled                       \
    -Dvapoursynth=disabled                \
    -Dcaca=disabled                       \
    -Dsixel=disabled                      \
    -Djack=disabled                       \
    -Dopenal=disabled                     \
    -Dsdl2-audio=disabled                 \
    -Dsdl2-gamepad=disabled               \
    -Dsdl2-video=disabled
ninja
popd

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install

%post
update-desktop-database %{_datadir}/applications &>/dev/null || :
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f %{_datadir}/icons/hicolor || :
fi

%postun
update-desktop-database %{_datadir}/applications &>/dev/null || :
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f %{_datadir}/icons/hicolor || :
fi

%files
/usr/bin/mpv
%dir /usr/include/mpv
/usr/include/mpv/client.h
/usr/include/mpv/render.h
/usr/include/mpv/render_d3d11.h
/usr/include/mpv/render_gl.h
/usr/include/mpv/stream_cb.h
/usr/lib64/libmpv.so
/usr/lib64/libmpv.so.2
/usr/lib64/libmpv.so.2.6.0
/usr/lib64/pkgconfig/mpv.pc
/usr/share/applications/mpv.desktop
/usr/share/bash-completion/completions/mpv
%dir /usr/share/doc/mpv
/usr/share/doc/mpv/encoding-profiles.conf
/usr/share/doc/mpv/input.conf
/usr/share/doc/mpv/mplayer-input.conf
/usr/share/doc/mpv/mpv.conf
/usr/share/doc/mpv/restore-old-bindings.conf
/usr/share/doc/mpv/restore-osc-bindings.conf
/usr/share/fish/vendor_completions.d/mpv.fish
/usr/share/icons/hicolor/128x128/apps/mpv.png
/usr/share/icons/hicolor/16x16/apps/mpv.png
/usr/share/icons/hicolor/32x32/apps/mpv.png
/usr/share/icons/hicolor/64x64/apps/mpv.png
/usr/share/icons/hicolor/scalable/apps/mpv.svg
/usr/share/icons/hicolor/symbolic/apps/mpv-symbolic.svg
/usr/share/man/man1/mpv.1.gz
/usr/share/metainfo/mpv.metainfo.xml
/usr/share/zsh/site-functions/_mpv

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 0.42.0-1
- New package: mpv 0.42.0, latest stable upstream, for the default
  desktop.  Built with X11/EGL and libplacebo OpenGL output, ALSA and
  PulseAudio, LuaJIT scripting, and ffmpeg/libass/libarchive/libcurl.
  Vulkan and VA-API are disabled because the distribution does not ship
  a Vulkan loader or a VA-API-enabled ffmpeg.
