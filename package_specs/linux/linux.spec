Name:       linux
Version:    7.3.1
Release:    3
Summary:    Linux kernel
License:    GPL-2.0-only
Prefix:     /usr
Source0:    linux-%{version}.tar.xz
Source1:    linux-%{version}.config
BuildRequires: xz

%description
General-purpose Linux kernel for Tenko Linux.  The configuration is
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
# Tenko has no SELinux: keep it disabled even if a future config update
# or Kconfig default tries to turn it back on.
scripts/config --disable SECURITY_SELINUX
# No module signing.  The distro does not ship a Secure Boot shim or an
# enrolled MOK, so signing the kernel/modules would only add a key-management
# burden without enabling Secure Boot.  Out-of-tree modules are accepted.
scripts/config --disable MODULE_SIG
scripts/config --disable MODULE_SIG_FORCE
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
Requires:   linux-modules = %{version}-%{release}
%description kernel
Linux kernel image (vmlinuz).

%files kernel
/boot/vmlinuz-%{version}

%post kernel
# systemd-boot reads loader entries from the ESP, which the installer mounts
# at /boot.  /etc/kernel/cmdline is written there with the root UUID; reuse it
# so upgrading the kernel adds an entry for the new image.  Systems that do not
# boot through systemd-boot have no loader directory and are left alone.
if [ -d /boot/loader/entries ] && [ -f /etc/kernel/cmdline ]; then
    cmdline=$(tr '\n' ' ' < /etc/kernel/cmdline)
    cat > "/boot/loader/entries/tenko-%{version}.conf" <<TENKO_EOF
title Tenko Linux 13.1 (%{version})
linux /vmlinuz-%{version}
initrd /initramfs-%{version}.img
options $cmdline
TENKO_EOF
fi

%preun kernel
if [ "$1" = 0 ]; then
    rm -f "/boot/loader/entries/tenko-%{version}.conf"
fi

%package kernel-debug
Summary:    Linux kernel symbol map and configuration
Requires:   linux-kernel = %{version}-%{release}
%description kernel-debug
The System.map and .config that belong to the installed kernel image.  They
are split out because they are only needed for debugging and driver builds,
not for booting.

%files kernel-debug
/boot/System.map-%{version}
/boot/config-%{version}

%package modules
Summary:    Linux kernel modules
Requires(post): kmod
# dracut supplies /etc/dracut.conf.d/10-tenko.conf (hostonly=no) and the
# initramfs generator used by the post-install scriptlet below.
Requires(post): dracut
%description modules
Linux kernel modules.

%files modules
/usr/lib/modules/%{version}/

%post modules
depmod %{version} >/dev/null 2>&1 || :

# Generate the initial ramdisk for this kernel.  This is a distro with a
# modular general-purpose kernel, so a new kernel without an initramfs is not
# bootable on most real hardware (the QEMU image is the exception because
# virtio-blk/ext4 are built in).
if [ -x /usr/bin/dracut ]; then
    /usr/bin/dracut --force --kver %{version} \
        /boot/initramfs-%{version}.img || \
        echo "tenko: dracut failed for %{version}; keep an existing initramfs" >&2
fi

%preun modules
if [ "$1" = 0 ]; then
    rm -f /boot/initramfs-%{version}.img
fi

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 7.3.1-3
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-only): COPYING, which states GPL version 2 only (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 7.3.1-2
- Add loader entries for systemd-boot: %post kernel writes
  /boot/loader/entries/browneye-<kver>.conf from /etc/kernel/cmdline when the
  ESP is mounted at /boot, and %preun removes it.  Part of the systemd-boot
  conversion (docs/systemd-boot.md); systems with GRUB have no loader
  directory and are unaffected.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 7.3.1-1
- Sync with LFS r13.1

* Mon Nov 02 2026 browneye <build@browneye.invalid> 7.2.6-5
- Set CONFIG_DRM_PANIC_SCREEN="user": the sanitized config selected the
  qr_code formatter while CONFIG_DRM_PANIC_SCREEN_QR_CODE is off (it needs
  Rust), so the kernel logged a fallback warning at boot

* Sun Nov 01 2026 browneye <build@browneye.invalid> 7.2.6-4
- Bump the release for the linux-kernel-debug split: the 7.2.6-3 build is
  already published with the old monolithic payload, so the split needs a
  new NEVR for upgrades to install it

* Sun Nov 01 2026 browneye <build@browneye.invalid> 7.2.6-3
- Split /boot/System.map-%{version} and /boot/config-%{version} into
  linux-kernel-debug; linux-kernel keeps the vmlinuz image
- Generate /boot/initramfs-%{version}.img automatically in the modules
  post-install scriptlet (dracut, generic hostonly=no image), and remove it
  on erase
- Make the kernel image package require linux-modules; modules require
  dracut at install time
- Disable module signing explicitly.  Browneye ships no Secure Boot shim or
  enrolled MOK, so module signing is not enforced (documented decision)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 7.2.6-2
- Adopt the sanitized Fedora 44 host config as the general-purpose baseline
  (debug info, SELinux/IMA, lockdown/signing, Rust/BTF, UBSAN and MAXSMP off)
- Keep virtio-blk, ext4, 9p and virtio-gpu built in for the QEMU test image

* Fri Oct 30 2026 browneye <build@browneye.invalid> 7.1.8
- Sync with LFS r13.1; QEMU/virtio boot configuration
