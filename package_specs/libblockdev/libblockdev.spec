Name:       libblockdev
Version:    3.5.0
Release:    1
Summary:    Library for low-level block device management
License:    LGPL-2.1-or-later
URL:        https://github.com/storaged-project/libblockdev
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

Requires:   libbytesize
Requires:   libatasmart
Requires:   keyutils
Requires:   libnvme
Requires:   json-glib
Requires:   cryptsetup
Requires:   LVM2
Requires:   e2fsprogs
Requires:   util-linux
Requires:   btrfs-progs
Requires:   mdadm
Requires:   dosfstools

%description
libblockdev is a C library that provides a stable interface for low-level
block device operations: partitioning, filesystem creation and mounting,
LUKS encryption, swap, loop devices, device-mapper, LVM and software RAID.

The library loads its backends as plugins.  This package contains the core
library, the plugin modules and the development files; the plugins for
filesystems, partitions, loop devices, crypto, swap, LVM, device-mapper,
mdraid, btrfs, NVMe and ATA SMART are enabled.

%prep
%setup -q

%build
%configure \
    --disable-static \
    --disable-introspection \
    --with-python3=no \
    --with-gtk-doc=no \
    --with-tools=no \
    --with-escrow=no \
    --with-s390=no \
    --with-nvdimm=no \
    --with-lvm_dbus=no \
    --with-smartmontools=no \
    --with-nvme=yes \
    --with-smart=yes \
    --with-btrfs=yes \
    --with-crypto=yes \
    --with-dm=yes \
    --with-loop=yes \
    --with-lvm=yes \
    --with-mdraid=yes \
    --with-mpath=no \
    --with-swap=yes \
    --with-part=yes \
    --with-fs=yes
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libblockdev.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 3.5.0-1
- Initial package at the latest stable upstream release, 3.5.0.
- Verified the licence as LGPL-2.1-or-later from LICENSE and the
  source file headers.
- Folded the upstream runtime plugin split and the -devel payload into
  the main package; this distro has no -devel subpackages.
- Enabled the btrfs, crypto, dm, fs, loop, lvm, mdraid, nvme, part,
  smart and swap plugins.  Disabled mpath (no multipath-tools package),
  lvm_dbus (no lvmdbusd), nvdimm (no ndctl), s390 (other architecture),
  escrow (no libvolume_key) and smartmontools (no smartmontools
  package).
