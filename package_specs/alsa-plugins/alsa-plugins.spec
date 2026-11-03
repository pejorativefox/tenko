Name:       alsa-plugins
Version:    1.2.12
Release:    1
Summary:    ALSA sound interface plugins.
License:    GPL
Source0:    %{name}-%{version}.tar.bz2
Source1:    %{name}-%{version}-ffmpeg-9.0.patch
Prefix:     /usr

%description
 The ALSA Plugins package contains plugins for various audio libraries and sound servers.

%prep
%setup -q
patch -Np1 -i %{SOURCE1}

%build
%configure --sysconfdir=/etc
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/etc/alsa/conf.d/10-speexrate.conf
/etc/alsa/conf.d/50-arcam-av-ctl.conf
/etc/alsa/conf.d/50-oss.conf
/etc/alsa/conf.d/50-pulseaudio.conf
/etc/alsa/conf.d/60-upmix.conf
/etc/alsa/conf.d/60-vdownmix.conf
/etc/alsa/conf.d/98-usb-stream.conf
/etc/alsa/conf.d/99-pulseaudio-default.conf.example
/usr/lib64/alsa-lib/libasound_module_conf_pulse.so
/usr/lib64/alsa-lib/libasound_module_ctl_arcam_av.so
/usr/lib64/alsa-lib/libasound_module_ctl_oss.so
/usr/lib64/alsa-lib/libasound_module_ctl_pulse.so
/usr/lib64/alsa-lib/libasound_module_pcm_oss.so
/usr/lib64/alsa-lib/libasound_module_pcm_pulse.so
/usr/lib64/alsa-lib/libasound_module_pcm_upmix.so
/usr/lib64/alsa-lib/libasound_module_pcm_usb_stream.so
/usr/lib64/alsa-lib/libasound_module_pcm_vdownmix.so
/usr/lib64/alsa-lib/libasound_module_rate_speexrate.so
/usr/lib64/alsa-lib/libasound_module_rate_speexrate_best.so
/usr/lib64/alsa-lib/libasound_module_rate_speexrate_medium.so
/usr/share/alsa/alsa.conf.d/10-speexrate.conf
/usr/share/alsa/alsa.conf.d/50-arcam-av-ctl.conf
/usr/share/alsa/alsa.conf.d/50-oss.conf
/usr/share/alsa/alsa.conf.d/50-pulseaudio.conf
/usr/share/alsa/alsa.conf.d/60-upmix.conf
/usr/share/alsa/alsa.conf.d/60-vdownmix.conf
/usr/share/alsa/alsa.conf.d/98-usb-stream.conf

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.2.12-1
- Sync with BLFS r13.1

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.1.6
- Initial RPM

