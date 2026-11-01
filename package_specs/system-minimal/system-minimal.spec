Name:       system-minimal
Version:    0.1
Release:    2
Summary:    Meta-package for minimal system.
License:    MIT

Requires: browneye-release browneye-sysconfig browneye-firstboot dnf make-ca shadow linux-pam
Requires: NetworkManager, polkit, linux-kernel, linux-modules, linux-firmware
Requires: finit, p11-kit, grep, findutils, grep, sed e2fsprogs sysklogd dhcp
Requires: inetutils, wpa-supplicant, vim, iana-etc

%description
A meta-package to install a minimal functional system.

%prep

%build

%install

%files

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.1-2
- Require browneye-firstboot (E5 root password policy)

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 0.1
- Initial RPM

