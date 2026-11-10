Name:       pulseaudio-bluez
Version:    17.0
Release:    1
Summary:    PulseAudio Bluetooth audio modules (A2DP/HFP)
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    pulseaudio-%{version}.tar.xz
BuildRequires: libsndfile
BuildRequires: sbc
BuildRequires: bluez
Requires:   pulseaudio = %{version}
Requires:   bluez

%description
The PulseAudio BlueZ 5 backend: module-bluetooth-policy,
module-bluetooth-discover, module-bluez5-discover and module-bluez5-device.
default.pa loads the policy and discover modules when their files exist,
which turns paired A2DP sinks and HFP headsets into ordinary PulseAudio
devices.

The modules are built from the pulseaudio source but shipped separately: the
pulseaudio package's own build needs perl XML::Parser to generate its manual
pages, and this build generates none.  The pulseaudio version is pinned so
the module ABI cannot drift.

%prep
%setup -q -n pulseaudio-%{version}

%build
mkdir build
pushd build
meson setup ..                    \
      --prefix=/usr               \
      --buildtype=release         \
      -D database=gdbm            \
      -D doxygen=false            \
      -D man=false                \
      -D bluez5=enabled           \
      -D bluez5-native-headset=true \
      -D bluez5-ofono-headset=false \
      -D tests=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot}/stage ninja install
popd
install -vdm755 %{buildroot}%{_libdir}/pulseaudio/modules
for module in module-bluetooth-discover module-bluetooth-policy \
              module-bluez5-discover module-bluez5-device \
              libbluez5-util; do
    install -vm755 %{buildroot}/stage/usr/lib64/pulseaudio/modules/$module.so \
        %{buildroot}%{_libdir}/pulseaudio/modules/
done
rm -rf %{buildroot}/stage

%files
%{_libdir}/pulseaudio/modules/libbluez5-util.so
%{_libdir}/pulseaudio/modules/module-bluetooth-discover.so
%{_libdir}/pulseaudio/modules/module-bluetooth-policy.so
%{_libdir}/pulseaudio/modules/module-bluez5-discover.so
%{_libdir}/pulseaudio/modules/module-bluez5-device.so

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 17.0-1
- New package: the PulseAudio BlueZ 5 modules, built from pulseaudio 17.0
  (latest stable upstream) with bluez5=enabled and the native headset
  backend.  Split from pulseaudio so the main package's man-page build,
  which needs a perl XML::Parser that Tenko does not package, is untouched.
