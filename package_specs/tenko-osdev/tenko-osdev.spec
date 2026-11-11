Name:       tenko-osdev
Version:    6
Release:    4
Epoch:      1
Summary:    Tenko Linux OS development environment
License:    MIT
URL:        https://github.com/pejorativefox/tenko
Prefix:     /usr

# The full base, which includes the development environment
# (tenko-base-build) and the toolchain baseline with dnf and createrepo_c
# (tenko-buildroot).
Requires:   tenko-base

# Container runtime: every `tenko build`, `tenko image` and QEMU helper
# runs in podman.
Requires:   podman-bin

# Network debugging and talking to QEMU monitor/serial sockets.
Requires:   ncat
Requires:   socat

# Publishing to R2 and the LAN mirror.
Requires:   rclone
Requires:   rsync
Requires:   openssh

# Source and release downloads.
Requires:   git
Requires:   curl
Requires:   wget

# ISO authoring tools.  `tenko image iso` installs these into its tools
# container from a staged local repository, so having them on the host also
# makes the individual steps usable directly.
Requires:   libisoburn
Requires:   squashfs-tools
Requires:   mtools
Requires:   dosfstools

# Initramfs and image/VM testing.
Requires:   dracut
Requires:   cpio
Requires:   zstd
Requires:   qemu
Requires:   edk2-ovmf

%description
The Tenko OS development environment: everything needed on a Tenko host to
build packages, assemble the RPM repository, produce the installer ISO and
container rootfs, and publish the results.

It pulls in the full base system, the compiler and RPM packaging toolchain
(tenko-base-build on tenko-buildroot, with dnf/createrepo_c), the static
podman bundle, ncat,
rclone and OpenSSH for publishing, the ISO authoring tools (libisoburn,
squashfs-tools, mtools, dosfstools), dracut/cpio for the live initramfs, and
QEMU with OVMF for boot testing.

tenko-rpm-config arrives through tenko-base-build; it uses the same
/var/lib/rpm database path as installed Tenko systems, so adding this meta
to an existing system does not move the RPM database.

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/tenko
touch %{buildroot}/usr/share/tenko/osdev

%files -f %{_sourcedir}/tenko-osdev.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 6-4
- Require socat (new package) for QEMU monitor and serial sockets.

* Wed Nov 11 2026 tenko <build@tenko.invalid> 6-3
- Drop the tenko-base-build and tenko-build requirements: tenko-base now
  requires tenko-base-build, which layers on tenko-buildroot (the new home
  of dnf and createrepo_c).
- Require ncat, moved out of tenko-base.

* Mon Nov 09 2026 browneye <build@browneye.invalid> 6-2
- Rebuild against tenko-rpm-config 6-2: the RPM database path is now
  /var/lib/rpm (the installed-system default), so installing this meta no
  longer requires a database migration.

* Mon Nov 09 2026 browneye <build@browneye.invalid> 6-1
- New meta-package for OS development on Tenko: full base, the build and
  RPM/repodata toolchain, podman, publish clients, ISO authoring tools and
  QEMU/OVMF for image testing.  This is the environment the ISO and rootfs
  build scripts expect, including tenko-rpm-config for a consistent RPM
  database path between host and installroot.
