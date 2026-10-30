Name:       linux
Version:    7.1.8
Release:    1
Summary:    Linux kernel
License:    GPL2
Prefix:     /usr
Source0:    linux-%{version}.tar.xz
Source1:    linux-%{version}.config

%description
Linux kernel for Browneye Linux, built for QEMU/virtio boot testing.

%prep
%setup -q -n linux-%{version}

%build
make mrproper
cp -v %{SOURCE1} .config
for opt in \
    VIRTIO VIRTIO_PCI VIRTIO_BLK VIRTIO_NET VIRTIO_CONSOLE \
    HW_RANDOM_VIRTIO PCI PCI_MSI \
    SERIAL_8250 SERIAL_8250_CONSOLE \
    DEVTMPFS DEVTMPFS_MOUNT TMPFS \
    EXT4_FS \
    NET_9P NET_9P_VIRTIO 9P_FS ; do
    scripts/config --enable "$opt"
done
make olddefconfig
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/boot
install -m644 arch/x86/boot/bzImage %{buildroot}/boot/vmlinuz-%{version}
install -m644 System.map %{buildroot}/boot/System.map-%{version}
install -m644 .config %{buildroot}/boot/config-%{version}
make INSTALL_MOD_PATH=%{buildroot}/usr modules_install
rm -f %{buildroot}/usr/lib/modules/%{version}/build \
      %{buildroot}/usr/lib/modules/%{version}/source

%package kernel
Summary:    Linux kernel image
%description kernel
Linux kernel image, System.map, and configuration.

%files kernel
/boot/vmlinuz-%{version}
/boot/System.map-%{version}
/boot/config-%{version}

%package modules
Summary:    Linux kernel modules
%description modules
Linux kernel modules.

%files modules
/usr/lib/modules/%{version}/

%post modules
depmod %{version}

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 7.1.8
- Sync with LFS r13.1; QEMU/virtio boot configuration
