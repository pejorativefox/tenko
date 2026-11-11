Name:       pulseaudio
Version:    17.0
Release:    2
Summary:    Networked low-latency sound server
License:    LGPL-2.1-or-later
URL:        https://gitlab.freedesktop.org/pulseaudio/pulseaudio
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

BuildRequires: libsndfile

%description
PulseAudio is a networked low-latency sound server for Linux, POSIX and
Windows systems. It provides audio playback, recording, mixing and network
streaming for desktop applications.

%prep
%setup 

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -D database=gdbm    \
      -D doxygen=false    \
      -D bluez5=disabled  \
      -D tests=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -f %{buildroot}/usr/share/dbus-1/system.d/pulseaudio-system.conf

%files -f %{_sourcedir}/pulseaudio.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 17.0-2
- Replace the TODO summary/description and record the verified license
  (LGPL-2.1-or-later): LICENSE (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 17.0-1
- Sync with the base set

# let's skip this for now

