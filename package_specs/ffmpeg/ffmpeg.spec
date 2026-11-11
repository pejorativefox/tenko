Name:       ffmpeg
Version:    9.0.2
Release:    3
Summary:    Multimedia framework for audio and video processing
License:    GPL-3.0-or-later
URL:        https://ffmpeg.org/
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
Patch0:     %{name}-%{version}-chromium_method-1.patch

BuildRequires: libtheora
BuildRequires: libvorbis
BuildRequires: libva
BuildRequires: libx264
BuildRequires: alsa-lib
BuildRequires: freetype
BuildRequires: lame
BuildRequires: libass
BuildRequires: libdrm
BuildRequires: libvpx
BuildRequires: libx11
BuildRequires: libxcb
BuildRequires: openssl
BuildRequires: fontconfig
BuildRequires: fribidi
BuildRequires: harfbuzz
BuildRequires: libXdmcp
BuildRequires: libogg
BuildRequires: libpciaccess
BuildRequires: libpng
BuildRequires: libxau
BuildRequires: xorgproto
BuildRequires: nasm
BuildRequires: texinfo

%description
FFmpeg is a collection of libraries and tools to process multimedia content
such as audio, video, subtitles and related metadata. It provides the
libavcodec, libavformat, libavutil, libavfilter, libavdevice, libswresample
and libswscale libraries, together with the ffmpeg, ffplay and ffprobe
tools.  This build includes VA-API hardware encoding/decoding for AMD
and Intel GPUs and the libx264 software H.264 encoder.

%prep
%setup -q
%patch -P 0 -p1 -F2

%build
./configure --prefix=/usr             \
            --enable-gpl              \
            --enable-version3         \
            --enable-nonfree          \
            --disable-static          \
            --enable-shared           \
            --disable-debug           \
            --enable-libass           \
            --enable-libfreetype      \
            --enable-libmp3lame       \
            --enable-libvorbis        \
            --enable-libvpx           \
            --enable-openssl          \
            --enable-vaapi            \
            --enable-libx264          \
            --disable-vulkan          \
            --disable-nvenc           \
            --ignore-tests=enhanced-flv-av1,enhanced-flv-multitrack \
            --docdir=/usr/share/doc/ffmpeg-%{version}
%make_build
gcc tools/qt-faststart.c -o tools/qt-faststart

%install
rm -rf %{buildroot}
%make_install
install -m755 tools/qt-faststart %{buildroot}%{_bindir}/qt-faststart
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/ffmpeg.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 9.0.2-3
- Enable VA-API (--enable-vaapi) and the libx264 software H.264 encoder
  (--enable-libx264).  gpu-screen-recorder uses FFmpeg's h264_vaapi,
  hevc_vaapi, av1_vaapi, vp8_vaapi and vp9_vaapi encoders, and libx264
  for its CPU fallback; without these the recorder has no usable video
  encoder at all.  Vulkan and NVENC are disabled explicitly: Tenko ships
  no NVIDIA driver stack, and enabling them would otherwise depend on
  whatever headers happen to be installed in the build image.  The
  library sonames and the package file list are unchanged.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 9.0.2-2
- Replace the TODO summary/description and record the verified license
  (GPL-3.0-or-later): LICENSE.md (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 9.0.2-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.1.1
- Initial RPM

