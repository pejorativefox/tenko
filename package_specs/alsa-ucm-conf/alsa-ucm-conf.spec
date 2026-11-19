Name:       alsa-ucm-conf
Version:    1.2.16.1
Release:    1
Summary:    ALSA Use Case Manager configuration
License:    BSD-3-Clause
URL:        https://github.com/alsa-project/alsa-ucm-conf
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr
BuildArch:  noarch

Requires:   alsa-lib

AutoProv:   no
AutoReq:    no

# BuildRequires: none (toolchain only)

%description
The ALSA Use Case Manager configuration files.  UCM describes how the
controls of a sound card map to use cases such as speakers, headphones,
the internal microphone and HDMI output, and libasound uses it to switch
between them.

The Intel/sof-hda-dsp profile is what makes the SOF HDA sound card route
audio to the right output; without it PulseAudio sees the card but cannot
activate speakers or headphones.  The ucm2 tree also carries profiles for
the other HDA, USB and ASoC codecs supported by alsa-lib.

%prep
%setup -q

%build
# Configuration data: nothing to compile.

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_datadir}/alsa
cp -a ucm ucm2 %{buildroot}%{_datadir}/alsa/

install -d %{buildroot}%{_datadir}/licenses/%{name}
install -m 0644 LICENSE %{buildroot}%{_datadir}/licenses/%{name}/

%files -f %{_sourcedir}/alsa-ucm-conf.filelist

%changelog
* Thu Nov 19 2026 tenko <build@tenko.invalid> 1.2.16.1-1
- New package, not in the base set: latest upstream stable release
  (1.2.16.1, matching alsa-lib, checked 2026-11-19).  Provides the UCM
  profiles the SOF HDA sound card needs to route speakers, headphones and
  microphones.
