Name:       sbc
Version:    2.2
Release:    1
Summary:    Bluetooth SBC audio codec library
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    sbc-%{version}.tar.xz

%description
SBC (Subband Coding) is the low-complexity audio codec that every A2DP
sink or source must support.  This package provides libsbc, used by the
PulseAudio and PipeWire Bluetooth backends to encode and decode A2DP
streams, together with the sbcinfo, sbcenc and sbcdec tools.

%prep
%setup -q

%build
%configure --prefix=/usr --disable-static --disable-tester
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/sbc.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 2.2-1
- New package: the SBC codec library the PulseAudio BlueZ backend needs
  (latest stable upstream, sbc 2.2).
