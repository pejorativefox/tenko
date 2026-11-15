Name:       pipewire
Version:    1.6.11
Release:    1
Summary:    Multimedia processing graph and server
License:    MIT
URL:        https://pipewire.org/
Source0:    pipewire-%{version}.tar.bz2
Prefix:     /usr
BuildRequires: alsa-lib
BuildRequires: dbus-daemon
BuildRequires: dbus-libs
BuildRequires: libcanberra
BuildRequires: libx11
BuildRequires: libxfixes
BuildRequires: openssl
BuildRequires: bluez
BuildRequires: gstreamer
BuildRequires: libdrm
BuildRequires: libopus
BuildRequires: libsndfile
BuildRequires: libusb
BuildRequires: pulseaudio
BuildRequires: sbc
BuildRequires: sdl2
BuildRequires: xorgproto
BuildRequires: gst-plugins-base

%description
PipeWire is a server and user space API to deal with multimedia
pipelines: audio and video capture, playback, and processing.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                 \
      --prefix=/usr            \
      --buildtype=release      \
      -D session-managers="[]" \
      -D bluez5=disabled         \
      -D gstreamer=disabled      \
      -D libpulse=disabled       \
      -D sndfile=disabled        \
      -D pw-cat=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/pipewire.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.6.11-1
- New package, required by xdg-desktop-portal
