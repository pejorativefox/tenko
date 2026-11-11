Name:       usbutils
Version:    020
Release:    2
Summary:    Utilities for Linux USB devices
License:    GPL-2.0-or-later
URL:        https://github.com/gregkh/usbutils
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

%files -f %{_sourcedir}/usbutils.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 020-2
- Replace NO_IDEA with the verified license (GPL-2.0-or-later): README.md SPDX header (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 020-1
- Sync with the base set

* Mon May 18 2020 Chris Statzer <chris.statzer@qq.com> 012
- Initial RPM

