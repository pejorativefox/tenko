Name:       udisks2
Version:    2.11.2
Release:    1
Summary:    Disk management service for desktop storage devices
License:    GPL-2.0-or-later
URL:        https://github.com/storaged-project/udisks
Source0:    udisks-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: glib
BuildRequires: libgudev
BuildRequires: polkit
BuildRequires: libblockdev
BuildRequires: util-linux
BuildRequires: systemd

Requires:   libblockdev
Requires:   libgudev
Requires:   polkit

%description
udisks2 is a D-Bus service that exposes storage devices to desktop
applications.  It enumerates disks and partitions, mounts and unmounts
filesystems, creates and edits partitions, manages loop devices and reports
drive health.  The service is D-Bus activated and runs as root; access is
controlled through polkit actions.

%prep
%setup -q -n udisks-%{version}

%build
%configure \
    --disable-static \
    --disable-gtk-doc \
    --disable-man \
    --enable-daemon \
    --enable-lvm2 \
    --enable-btrfs \
    --disable-iscsi \
    --disable-lsm \
    --with-udevdir=%{_prefix}/lib/udev \
    --with-systemdsystemunitdir=%{_unitdir} \
    --with-tmpfilesdir=/usr/lib/tmpfiles.d \
    --with-modloaddir=/usr/lib/modules-load.d \
    --with-modprobedir=/usr/lib/modprobe.d
%make_build

%install
rm -rf %{buildroot}
%make_install
# The pre-generated gtk-doc HTML is not part of the runtime service and
# would add several hundred files to the package.
rm -rf %{buildroot}%{_datadir}/gtk-doc

%files -f %{_sourcedir}/udisks2.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 2.11.2-1
- Initial package at the latest stable upstream release, 2.11.2 (the
  current 2.11 stable series, newer than the 2.10 series).
- Verified the licence as GPL-2.0-or-later from COPYING and the source
  file headers; the libudisks2 library is LGPL-2.0-or-later and is
  shipped in this same package.
- Built with the lvm2 and btrfs modules; iSCSI and LibStorageMgmt are
  disabled because libiscsi and libstoragemgmt are not packaged.
- Installed the D-Bus policy and activation file, systemd unit, polkit
  actions, udev rule, tmpfiles config and /etc/udisks2 configuration.
