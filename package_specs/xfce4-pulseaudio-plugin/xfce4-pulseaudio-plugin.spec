Name:       xfce4-pulseaudio-plugin
Version:    0.4.9
Release:    1
Summary:    PulseAudio volume control plugin for the Xfce panel
License:    GPL-2.0-or-later
URL:        https://docs.xfce.org/panel-plugins/xfce4-pulseaudio-plugin/start
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: exo
BuildRequires: libxfce4ui
BuildRequires: pulseaudio
BuildRequires: xfce4-panel
BuildRequires: xfconf

%description
A panel plugin for the Xfce panel to control the PulseAudio sound server.
It shows the current volume and mute state in the panel, provides a menu
for selecting output devices and MPRIS media players, and opens a mixer
when clicked.

%package lang
Summary:    xfce4-pulseaudio-plugin translations
Requires:   xfce4-pulseaudio-plugin = %{version}-%{release}

%description lang
Translations for xfce4-pulseaudio-plugin.

%prep
%setup

%build
%configure \
    --disable-keybinder \
    --disable-libcanberra
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install

%files -f %{_sourcedir}/xfce4-pulseaudio-plugin.filelist
%files lang -f %{_sourcedir}/xfce4-pulseaudio-plugin-lang.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 0.4.9-1
- Initial package, latest stable upstream release in the Xfce 4.20 series
  (0.4.9, released with Xfce 4.20 on 2024-12-05; the 0.5.x series targets
  the post-4.20 libxfce4ui 4.21 development cycle).
- Verify the SPDX licence expression from COPYING and the source headers:
  GPL-2.0-or-later (COPYING is GPL v2; all 26 .c/.h files carry the
  "either version 2 ... or (at your option) any later version" clause).
- Build with --disable-keybinder: keybinder-3.0 is not packaged in Tenko,
  so media-key handling falls back to the Xfce panel shortcuts.  Build
  with --disable-libcanberra: libcanberra is not in the build image, so
  volume changes do not play a system sound.
