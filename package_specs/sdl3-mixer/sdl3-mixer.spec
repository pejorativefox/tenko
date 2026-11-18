Name:       sdl3-mixer
Version:    3.2.4
Release:    1
Summary:    SDL3_mixer is an audio mixing library
License:    Zlib
URL:        https://github.com/libsdl-org/SDL_mixer
Source0:    SDL3_mixer-%{version}.tar.gz
Prefix:     /usr

BuildRequires: sdl3
BuildRequires: flac
BuildRequires: libvorbis

# game-music-emu, libxmp, opusfile, mpg123, WavPack and FluidSynth are not
# in the distro; those formats are disabled explicitly so the strict
# dependency check does not see them.  MIDI is off because the bundled
# timidity ships no instrument data.
%description
SDL3_mixer is an audio mixing library that plays WAVE, AIFF, VOC, AU,
MP3, Ogg Vorbis and FLAC files.

%prep
%setup -q -n SDL3_mixer-%{version}

%build
mkdir build
pushd build
cmake -D CMAKE_INSTALL_PREFIX=/usr \
      -D CMAKE_INSTALL_LIBDIR=lib64 \
      -D CMAKE_BUILD_TYPE=Release \
      -D SDLMIXER_DEPS_SHARED=OFF \
      -D SDLMIXER_STRICT=ON \
      -D SDLMIXER_MP3_MPG123=OFF \
      -D SDLMIXER_VORBIS_STB=OFF \
      -D SDLMIXER_FLAC_DRFLAC=OFF \
      -D SDLMIXER_GME=OFF \
      -D SDLMIXER_MOD=OFF \
      -D SDLMIXER_OPUS=OFF \
      -D SDLMIXER_WAVPACK=OFF \
      -D SDLMIXER_MIDI=OFF \
      -W no-author -G Ninja ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/sdl3-mixer.filelist

%changelog
* Wed Nov 18 2026 browneye <build@browneye.invalid> 3.2.4-1
- New package, not in the base set: latest upstream stable release
  (3.2.4, checked 2026-11-18).
- Link libFLAC and libvorbisfile directly (SDLMIXER_DEPS_SHARED=OFF) so
  rpm tracks the codec dependencies; MP3 uses the bundled dr_mp3 decoder.
- Disable game-music-emu, libxmp, opusfile, mpg123, WavPack and
  FluidSynth support (not in the distro) and MIDI (the bundled timidity
  ships no instrument data).
