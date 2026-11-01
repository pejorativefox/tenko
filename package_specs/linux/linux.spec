Name:       linux
Version:    7.2.6
Release:    2
Summary:    Linux kernel
License:    GPL2
Prefix:     /usr
Source0:    linux-%{version}.tar.xz
Source1:    linux-%{version}.config
BuildRequires: xz

%description
General-purpose Linux kernel for Browneye Linux.  The configuration is
based on the Fedora 44 host kernel config, forward-ported to this version
and sanitized for our packaging (no debug info, no SELinux/IMA, no module
signing, no Rust/BTF).

%prep
%setup -q -n linux-%{version}

%build
make mrproper
cp -v %{SOURCE1} .config
# Keep the direct-kernel QEMU test image self-contained: root on virtio-blk,
# the 9p debug share, and virtio-gpu built in.  The rest of the hardware
# support comes from the general config as modules.
for opt in \
    VIRTIO_PCI VIRTIO_BLK VIRTIO_CONSOLE \
    DRM_VIRTIO_GPU DRM_VGEM DRM_BOCHS DRM_GEM_SHMEM_HELPER \
    SERIAL_8250 SERIAL_8250_CONSOLE \
    DEVTMPFS DEVTMPFS_MOUNT TMPFS \
    EXT4_FS MODULE_COMPRESS_ALL \
    NET_9P NET_9P_VIRTIO 9P_FS ; do
    scripts/config --enable "$opt"
done
# Browneye has no SELinux: keep it disabled even if a future config update
# or Kconfig default tries to turn it back on.
scripts/config --disable SECURITY_SELINUX
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
Requires(post): kmod
%description modules
Linux kernel modules.

%files modules
/usr/lib/modules/%{version}/

%post modules
depmod %{version}

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 7.2.6-2
- Adopt the sanitized Fedora 44 host config as the general-purpose baseline
  (debug info, SELinux/IMA, lockdown/signing, Rust/BTF, UBSAN and MAXSMP off)
- Keep virtio-blk, ext4, 9p and virtio-gpu built in for the QEMU test image

* Fri Oct 30 2026 browneye <build@browneye.invalid> 7.1.8
- Sync with LFS r13.1; QEMU/virtio boot configuration
