Name:       usbutils
Version:    020
Release:    2
Summary:    Utilities for Linux USB devices
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The USB Utils package contains utilities used to display information about USB buses in the system and the devices connected to them.

%prep
%setup

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files
/usr/bin/lsusb
/usr/bin/lsusb.py
/usr/bin/usb-devices
/usr/bin/usbhid-dump
/usr/share/man/man1/lsusb.py.1.gz
/usr/share/man/man1/usb-devices.1.gz
/usr/share/man/man8/lsusb.8.gz
/usr/share/man/man8/usbhid-dump.8.gz

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 020-2
- Replace NO_IDEA with the verified license (GPL-2.0-or-later): README.md SPDX header (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 020-1
- Sync with BLFS r13.1

* Mon May 18 2020 Chris Statzer <chris.statzer@qq.com> 012
- Initial RPM

