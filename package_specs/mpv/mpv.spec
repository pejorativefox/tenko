Name:       mpv
Version:    0.42.0
Release:    2
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
BuildRequires: git
BuildRequires: libxfixes
BuildRequires: libxpresent
BuildRequires: openssl

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

%files -f %{_sourcedir}/mpv.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 0.42.0-2
- Drop the manual update-desktop-database and gtk-update-icon-cache
  calls; desktop-file-utils and gtk+ now provide file triggers for the
  desktop entry database and icon theme caches (issue #35).

* Sat Nov 07 2026 tenko <build@tenko.invalid> 0.42.0-1
- New package: mpv 0.42.0, latest stable upstream, for the default
  desktop.  Built with X11/EGL and libplacebo OpenGL output, ALSA and
  PulseAudio, LuaJIT scripting, and ffmpeg/libass/libarchive/libcurl.
  Vulkan and VA-API are disabled because the distribution does not ship
  a Vulkan loader or a VA-API-enabled ffmpeg.
