Name:       xfce-desktop-hardware
Version:    4.20
Release:    1
Summary:    Hardware extras for the Browneye XFCE desktop
License:    MIT
Prefix:     /usr

# D25: the firmware vendor packs are the hardware-dependent part of a
# desktop install, so they live in their own tiers instead of being hard
# requirements of every desktop.
Requires:   systemd-hwdb
Requires:   mesa
Requires:   linux-firmware-base
Requires:   linux-firmware-intel-wifi
Requires:   linux-firmware-nvidia
Requires:   linux-firmware-amd-gpu
Requires:   linux-firmware-intel-gpu
Requires:   linux-firmware-mediatek
Requires:   linux-firmware-ath
Requires:   linux-firmware-bluetooth
Requires:   linux-firmware-nic
Requires:   linux-firmware-other

%description
Hardware enablement for the Browneye XFCE desktop: the udev hardware
database, the Mesa userspace (llvmpipe and GPU drivers) and every
linux-firmware vendor pack (Intel Wi-Fi/GPU, NVIDIA, AMD GPU, MediaTek,
Atheros, Bluetooth, NIC and misc).

Install this on physical hardware.  It is pulled in by xfce-desktop-full
and can be added to a xfce-desktop-core install with
"dnf install xfce-desktop-hardware".

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/browneye
touch %{buildroot}/usr/share/browneye/xfce-desktop-hardware

%files
/usr/share/browneye/xfce-desktop-hardware

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.20-1
- New hardware profile: systemd-hwdb, Mesa and all linux-firmware vendor
  packs as hard requirements (plan D25)
