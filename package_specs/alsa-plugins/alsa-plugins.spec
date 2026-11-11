Name:       alsa-plugins
Version:    1.2.12
Release:    2
Summary:    ALSA sound interface plugins.
License:    LGPL-2.1-or-later AND GPL-2.0-or-later AND BSD-3-Clause
URL:        https://github.com/alsa-project/alsa-plugins
Source0:    %{name}-%{version}.tar.bz2
Patch0:     %{name}-%{version}-ffmpeg-9.0.patch
Prefix:     /usr

%description
 The ALSA Plugins package contains plugins for various audio libraries and sound servers.

%prep
%setup -q
%patch -P 0 -p1

%build
%configure --sysconfdir=/etc
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/alsa-plugins.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.12-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later AND GPL-2.0-or-later AND BSD-3-Clause): COPYING, COPYING.GPL, usb_stream/usb_stream.h and pph/speex_resampler.h (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.2.12-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 1.1.6
- Initial RPM

