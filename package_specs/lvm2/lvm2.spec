Name:       LVM2
Version:    2.03.44
Release:    1
Summary:    LVM2 logical volume management tools and device-mapper library
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
URL:        https://sourceware.org/lvm2/
Source0:    %{name}.%{version}.tgz
Prefix:     /usr

BuildRequires: libaio
BuildRequires: readline
BuildRequires: systemd
BuildRequires: util-linux-devel

%description
The LVM2 package is a set of tools that manage logical partitions. It
allows spanning of file systems across multiple physical disks and disk
partitions and provides for dynamic growing or shrinking of logical
partitions, mirroring and low storage footprint snapshots.

This package also provides the device-mapper library (libdevmapper).

%package devel
Summary:    Development files for LVM2 and libdevmapper
Requires:   %{name} = %{version}-%{release}

%description devel
Headers, pkg-config metadata and linker symlinks for libdevmapper and
liblvm2cmd.

%prep
%setup -q -n LVM2.%{version}

%build
# LVM2's configure detects system tools in /usr/sbin.
export PATH="$PATH:/usr/sbin"
%configure \
    --enable-cmdlib     \
    --enable-pkgconfig  \
    --enable-udev_sync  \
    --with-usrlibdir=%{_libdir}
%make_build

%install
rm -rf %{buildroot}
%make_install
# systemd revision of the BLFS instructions: install the units that
# activate logical volumes at boot (not installed by default).
make install_systemd_units DESTDIR=%{buildroot}
# BLFS systemd configuration step: the default locking_dir under /var/lock
# deadlocks at boot; use the runtime lock directory instead.
sed -e '/locking_dir =/{s/#//;s/var/run/}' \
    -i %{buildroot}%{_sysconfdir}/lvm/lvm.conf

%files -f %{_sourcedir}/lvm2.filelist
%files devel -f %{_sourcedir}/lvm2-devel.filelist

%changelog
* Mon Nov  2 2026 browneye <build@browneye.invalid> 2.03.44-1
- Update to 2.03.44 (current LFS/BLFS r13.1 trunk version).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.03.42-1
- Update to the BLFS r13.1 version (2.03.42, was 2.03.05)
- Enable cmdlib, pkgconfig and udev_sync as the book does; install the
  systemd units (systemd revision) and use the static filelist.
