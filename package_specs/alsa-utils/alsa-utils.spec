Name:       alsa-utils
Version:    1.2.16
Release:    2
Summary:    Alsa Utilities
License:    GPL-2.0-or-later AND LGPL-2.1-or-later AND BSD-3-Clause
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
The ALSA Utilities package contains various utilities which are useful for controlling your sound card. 

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files
/usr/bin/aconnect
/usr/bin/alsa-info.sh
/usr/bin/alsabat
/usr/bin/alsabat-test.sh
/usr/bin/alsaconf
/usr/bin/alsactl
/usr/bin/alsaloop
/usr/bin/alsamixer
/usr/bin/alsatplg
/usr/bin/alsaucm
/usr/bin/amidi
/usr/bin/amixer
/usr/bin/aplay
/usr/bin/aplaymidi
/usr/bin/aplaymidi2
/usr/bin/arecord
/usr/bin/arecordmidi
/usr/bin/arecordmidi2
/usr/bin/aseqdump
/usr/bin/aseqnet
/usr/bin/aseqsend
/usr/bin/axfer
/usr/bin/iecset
/usr/bin/nhlt-dmic-info
/usr/bin/speaker-test
/usr/lib/systemd/system/alsa-card-wait@.service
/usr/lib/systemd/system/alsa-restore.service
/usr/lib/systemd/system/alsa-state.service
/usr/lib/systemd/system/sound.target.wants/alsa-restore.service
/usr/lib/systemd/system/sound.target.wants/alsa-state.service
/usr/lib/udev/rules.d/90-alsa-restore.rules
/usr/lib64/alsa-topology/libalsatplg_module_nhlt.so
/usr/share/alsa/init/00main
/usr/share/alsa/init/ca0106
/usr/share/alsa/init/default
/usr/share/alsa/init/hda
/usr/share/alsa/init/help
/usr/share/alsa/init/info
/usr/share/alsa/init/test
/usr/share/locale/de/LC_MESSAGES/alsa-utils.mo
/usr/share/locale/eu/LC_MESSAGES/alsa-utils.mo
/usr/share/locale/fr/LC_MESSAGES/alsa-utils.mo
/usr/share/locale/ja/LC_MESSAGES/alsa-utils.mo
/usr/share/locale/ja/LC_MESSAGES/alsaconf.mo
/usr/share/locale/ka/LC_MESSAGES/alsa-utils.mo
/usr/share/locale/ka/LC_MESSAGES/alsaconf.mo
/usr/share/locale/ko/LC_MESSAGES/alsa-utils.mo
/usr/share/locale/ru/LC_MESSAGES/alsaconf.mo
/usr/share/locale/sk/LC_MESSAGES/alsa-utils.mo
/usr/share/man/fr/man8/alsaconf.8.gz
/usr/share/man/man1/aconnect.1.gz
/usr/share/man/man1/alsabat.1.gz
/usr/share/man/man1/alsactl.1.gz
/usr/share/man/man1/alsaloop.1.gz
/usr/share/man/man1/alsamixer.1.gz
/usr/share/man/man1/amidi.1.gz
/usr/share/man/man1/amixer.1.gz
/usr/share/man/man1/aplay.1.gz
/usr/share/man/man1/aplaymidi.1.gz
/usr/share/man/man1/aplaymidi2.1.gz
/usr/share/man/man1/arecord.1.gz
/usr/share/man/man1/arecordmidi.1.gz
/usr/share/man/man1/arecordmidi2.1.gz
/usr/share/man/man1/aseqdump.1.gz
/usr/share/man/man1/aseqnet.1.gz
/usr/share/man/man1/aseqsend.1.gz
/usr/share/man/man1/axfer-list.1.gz
/usr/share/man/man1/axfer-transfer.1.gz
/usr/share/man/man1/axfer.1.gz
/usr/share/man/man1/iecset.1.gz
/usr/share/man/man1/nhlt-dmic-info.1.gz
/usr/share/man/man1/speaker-test.1.gz
/usr/share/man/man8/alsa-info.sh.8.gz
/usr/share/man/man8/alsaconf.8.gz
/usr/share/sounds/alsa/Front_Center.wav
/usr/share/sounds/alsa/Front_Left.wav
/usr/share/sounds/alsa/Front_Right.wav
/usr/share/sounds/alsa/Noise.wav
/usr/share/sounds/alsa/Rear_Center.wav
/usr/share/sounds/alsa/Rear_Left.wav
/usr/share/sounds/alsa/Rear_Right.wav
/usr/share/sounds/alsa/Side_Left.wav
/usr/share/sounds/alsa/Side_Right.wav

/usr/share/man/man1/alsatplg.1.gz
/usr/share/man/man1/alsaucm.1.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.16-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND LGPL-2.1-or-later AND BSD-3-Clause): COPYING, alsaucm/usecase.c and topology/nhlt/nhlt.h (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.2.16-1
- Sync with the base set

* Thu May 28 2020 Chris Statzer <chris.statzer@qq.com> 1.2.2
- Initial RPM

