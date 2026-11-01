Name:       system-minimal
Version:    0.1
Release:    4
Summary:    Meta-package for minimal system.
License:    MIT

Requires: browneye-release browneye-sysconfig browneye-firstboot dnf make-ca shadow linux-pam
Requires: polkit linux-kernel linux-modules linux-firmware-base
Recommends: linux-firmware-intel-wifi, linux-firmware-nvidia, linux-firmware-amd-gpu
Recommends: linux-firmware-intel-gpu, linux-firmware-mediatek, linux-firmware-ath
Recommends: linux-firmware-bluetooth, linux-firmware-nic, linux-firmware-other
Requires: p11-kit grep findutils sed e2fsprogs
Requires: inetutils vim iana-etc

%description
A meta-package to install a minimal functional system.

%prep

%build

%install

%files

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.1-4
- Drop the five unsatisfiable Requires (NetworkManager, finit, sysklogd,
  dhcp, wpa-supplicant): none is built and finit/sysklogd are the removed
  sysvinit path.  The distro uses systemd-networkd/resolved for networking.
- Remove the duplicate grep entry.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.1-3
- Require linux-firmware-base and Recommend the vendor firmware packs

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.1-2
- Require browneye-firstboot (E5 root password policy)

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 0.1
- Initial RPM

