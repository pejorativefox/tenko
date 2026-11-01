# Source0: https://mirrors.edge.kernel.org/pub/linux/kernel/firmware/linux-firmware-20261019.tar.xz
#   sha256 a10d1ab5baf2c74ba92e8c7cf313e691696c26bddfa6df00db795e48d70cd4ca
# Source2: https://www.kernel.org/pub/software/network/wireless-regdb/wireless-regdb-2026.09.03.tar.xz
#   sha256 b22e0901227b820cd1c280abe681a15b773a5103a5e10dc442e94ebb34cbf58d

Name:       linux-firmware
%global regdb_version 2026.09.03
Version:    20261019
Release:    2
Summary:    Firmware files for Linux (curated subset)
License:    Redistributable, no modification permitted
URL:        https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
Source0:    %{name}-%{version}.tar.xz
Source1:    filter_whence.py
Source2:    wireless-regdb-%{regdb_version}.tar.xz
BuildArch:  noarch
Prefix:     /usr

%description
Curated subset of the Linux firmware repository for the hardware enabled by
the Browneye kernel: AMD, Intel and NVIDIA GPUs; Intel, MediaTek, Atheros,
Realtek, Broadcom, Cypress, Marvell and TI wireless; Bluetooth; Realtek
wired Ethernet; AMD CPU microcode; and the wireless regulatory database.

The full repository is about 2 GB; this subset is the common desktop and
laptop set and is installed compressed (xz) under /usr/lib/firmware.

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

%files
%license %{_datadir}/licenses/%{name}/LICENSE
%license %{_datadir}/licenses/%{name}/LICENSES
%license %{_datadir}/licenses/%{name}/LICENSE.wireless-regdb
%doc %{_datadir}/doc/%{name}/WHENCE
%{_prefix}/lib/firmware

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 20261019-2
- Include wireless-regdb 2026.09.03 (regulatory.db and signature)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 20261019
- Update to the 20261019 snapshot (sha256 a10d1ab5baf2c74ba92e8c7cf313e691696c26bddfa6df00db795e48d70cd4ca)
- Ship a curated desktop/laptop subset (GPUs, wireless, Bluetooth, NICs,
  microcode, regulatory database) instead of the 2023 partial copy
- Install under /usr/lib/firmware and compress with xz
