# Source0: https://mirrors.edge.kernel.org/pub/linux/kernel/firmware/linux-firmware-20261019.tar.xz
#   sha256 a10d1ab5baf2c74ba92e8c7cf313e691696c26bddfa6df00db795e48d70cd4ca
# Source2: https://www.kernel.org/pub/software/network/wireless-regdb/wireless-regdb-2026.09.03.tar.xz
#   sha256 b22e0901227b820cd1c280abe681a15b773a5103a5e10dc442e94ebb34cbf58d

Name:       linux-firmware
%global regdb_version 2026.09.03
Version:    20261019
Release:    3
Summary:    Firmware files for Linux (curated subset)
License:    Redistributable, no modification permitted
URL:        https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
Source0:    %{name}-%{version}.tar.xz
Source1:    filter_whence.py
Source2:    wireless-regdb-%{regdb_version}.tar.xz
BuildArch:  noarch
Prefix:     /usr

# The vendor subpackages carry the firmware files; linux-firmware itself is
# now only a meta-package so that "dnf install linux-firmware" still installs
# the complete set, while a consumer can select a single vendor pack.
Requires:   linux-firmware-base = %{version}-%{release}
Requires:   linux-firmware-intel-wifi = %{version}-%{release}
Requires:   linux-firmware-nvidia = %{version}-%{release}
Requires:   linux-firmware-amd-gpu = %{version}-%{release}
Requires:   linux-firmware-intel-gpu = %{version}-%{release}
Requires:   linux-firmware-mediatek = %{version}-%{release}
Requires:   linux-firmware-ath = %{version}-%{release}
Requires:   linux-firmware-bluetooth = %{version}-%{release}
Requires:   linux-firmware-nic = %{version}-%{release}
Requires:   linux-firmware-other = %{version}-%{release}

%description
Curated subset of the Linux firmware repository for the hardware enabled by
the Browneye kernel: AMD, Intel and NVIDIA GPUs; Intel, MediaTek, Atheros,
Realtek, Broadcom, Cypress, Marvell and TI wireless; Bluetooth; Realtek
wired Ethernet; AMD CPU microcode; and the wireless regulatory database.

The full repository is about 2 GB; this subset is the common desktop and
laptop set and is installed compressed (xz) under /usr/lib/firmware.

This package is a meta-package.  It requires every vendor subpackage so that
installing "linux-firmware" keeps installing the complete set.  Install
linux-firmware-base plus only the vendor pack(s) you need to save space.

%prep
%setup -q -n %{name}-%{version}
tar -xJf %{SOURCE2}

%build
# copy-firmware.sh does the copying, symlink creation and compression.

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_prefix}/lib/firmware

cp WHENCE WHENCE.orig
python3 %{SOURCE1}
cp WHENCE.filtered WHENCE
./copy-firmware.sh --xz %{buildroot}%{_prefix}/lib/firmware
mv WHENCE.orig WHENCE

install -D -m 0644 wireless-regdb-%{regdb_version}/regulatory.db %{buildroot}%{_prefix}/lib/firmware/regulatory.db
install -D -m 0644 wireless-regdb-%{regdb_version}/regulatory.db.p7s %{buildroot}%{_prefix}/lib/firmware/regulatory.db.p7s

install -d %{buildroot}%{_datadir}/licenses/%{name}
install -m 0644 LICENSE %{buildroot}%{_datadir}/licenses/%{name}/LICENSE
install -m 0644 wireless-regdb-%{regdb_version}/LICENSE %{buildroot}%{_datadir}/licenses/%{name}/LICENSE.wireless-regdb
cp -a LICENSES %{buildroot}%{_datadir}/licenses/%{name}/
install -D -m 0644 WHENCE %{buildroot}%{_datadir}/doc/%{name}/WHENCE

%package base
Summary:    Linux firmware: licences, WHENCE, regulatory database and CPU microcode
%description base
The vendor-independent part of the Linux firmware set: the licence files and
WHENCE, the wireless-regdb regulatory database (regulatory.db and its
signature), and the AMD CPU microcode.  This is everything required for
basic and regulatory operation; it is the only firmware package a virtual
machine needs.

%package intel-wifi
Summary:    Firmware for Intel wireless (iwlwifi)
Requires:   linux-firmware-base = %{version}-%{release}
%description intel-wifi
iwlwifi firmware for Intel wireless adapters (Wi-Fi 4 through Wi-Fi 7).

%package nvidia
Summary:    Firmware for NVIDIA GPUs (nouveau)
Requires:   linux-firmware-base = %{version}-%{release}
%description nvidia
NVIDIA GPU firmware used by nouveau, including the signed GA/GB/AD
generations.

%package amd-gpu
Summary:    Firmware for AMD GPUs (amdgpu and radeon)
Requires:   linux-firmware-base = %{version}-%{release}
%description amd-gpu
AMD GPU firmware for the amdgpu and radeon kernel drivers.

%package intel-gpu
Summary:    Firmware for Intel GPUs (i915 and xe)
Requires:   linux-firmware-base = %{version}-%{release}
%description intel-gpu
Intel GPU firmware for the i915 and xe kernel drivers.

%package mediatek
Summary:    Firmware for MediaTek wireless and connectivity
Requires:   linux-firmware-base = %{version}-%{release}
%description mediatek
MediaTek Wi-Fi and Bluetooth firmware (mt76 and friends).

%package ath
Summary:    Firmware for Qualcomm Atheros wireless (ath)
Requires:   linux-firmware-base = %{version}-%{release}
%description ath
Qualcomm Atheros wireless firmware: ath9k_htc, ath10k, ath11k, ath12k,
ath6k, their board data under qca/, and the wil6210 60 GHz firmware.

%package bluetooth
Summary:    Firmware for Realtek and Atheros Bluetooth controllers
Requires:   linux-firmware-base = %{version}-%{release}
%description bluetooth
Bluetooth firmware that lives in the vendor-neutral rtl_bt and ar3k
directories, plus the top-level ath3k-1.fw blob.

%package nic
Summary:    Firmware for Realtek wired Ethernet controllers
Requires:   linux-firmware-base = %{version}-%{release}
%description nic
Realtek rtl_nic firmware for the r8169 wired Ethernet driver.

%package other
Summary:    Remaining Linux firmware (Broadcom, Cypress, TI, Intel non-wifi, ...)
Requires:   linux-firmware-base = %{version}-%{release}
%description other
Everything not covered by a vendor pack: Broadcom/Cypress wireless,
Intel Bluetooth, camera, audio, QAT and other non-iwlwifi firmware, TI
connectivity, Marvell, Ralink, RSI, Atmel, Airoha and the miscellaneous
top-level blobs.

%files
%files base -f %{_sourcedir}/linux-firmware-base.filelist
%files intel-wifi -f %{_sourcedir}/linux-firmware-intel-wifi.filelist
%files nvidia -f %{_sourcedir}/linux-firmware-nvidia.filelist
%files amd-gpu -f %{_sourcedir}/linux-firmware-amd-gpu.filelist
%files intel-gpu -f %{_sourcedir}/linux-firmware-intel-gpu.filelist
%files mediatek -f %{_sourcedir}/linux-firmware-mediatek.filelist
%files ath -f %{_sourcedir}/linux-firmware-ath.filelist
%files bluetooth -f %{_sourcedir}/linux-firmware-bluetooth.filelist
%files nic -f %{_sourcedir}/linux-firmware-nic.filelist
%files other -f %{_sourcedir}/linux-firmware-other.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 20261019-3
- Split the single 395 MB package into linux-firmware-base (licences, WHENCE,
  regulatory database, AMD CPU microcode) and per-vendor packs: intel-wifi,
  nvidia, amd-gpu, intel-gpu, mediatek, ath, bluetooth, nic and other.
- linux-firmware is now a meta-package requiring base and every vendor pack,
  so "dnf install linux-firmware" is unchanged.
- Static filelists partition the previous package exactly (3722 paths).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 20261019-2
- Include wireless-regdb 2026.09.03 (regulatory.db and signature)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 20261019
- Update to the 20261019 snapshot (sha256 a10d1ab5baf2c74ba92e8c7cf313e691696c26bddfa6df00db795e48d70cd4ca)
- Ship a curated desktop/laptop subset (GPUs, wireless, Bluetooth, NICs,
  microcode, regulatory database) instead of the 2023 partial copy
- Install under /usr/lib/firmware and compress with xz
