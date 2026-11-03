Name:       qemu
Version:    11.1.3
Release:    1
Summary:    Open source machine emulator and virtualizer
License:    GPL-2.0-only AND LGPL-2.1-only
URL:        https://www.qemu.org/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: glib-devel
BuildRequires: pixman
BuildRequires: alsa-lib
BuildRequires: dtc
BuildRequires: libslirp

# The generic brp-strip pass also walks qemu's non-x86 firmware blobs
# (palcode-clipper, hppa-firmware*.img); the x86 strip binary cannot parse
# them and aborts the build.  The distro's custom strip already handled the
# real executables, so skip the redundant generic pass for this package.
%global __brp_strip %{nil}

%description
QEMU is a generic and open source machine emulator and virtualizer.  This
build targets x86_64 system emulation (hardware KVM acceleration, or TCG
when /dev/kvm is unavailable) and is what Browneye uses to boot and test
its images.  User-mode networking comes from libslirp, audio from ALSA,
and device trees from libfdt (dtc).

qemu-11.1.3 is the version in BLFS r13.1 (postlfs/virtualization/qemu).

%prep
%setup -q

%build
mkdir build
pushd build
../configure --prefix=/usr                \
             --sysconfdir=/etc            \
             --localstatedir=/var         \
             --target-list=x86_64-softmmu \
             --audio-drv-list=alsa        \
             --disable-download           \
             --disable-pa                 \
             --enable-slirp               \
             --docdir=/usr/share/doc/qemu-%{version}
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
%make_install
popd

%files -f %{_sourcedir}/qemu.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 11.1.3-1
- Update from the 8.1.0 stub to 11.1.3, the version in BLFS r13.1.
- Source: https://download.qemu.org/qemu-11.1.3.tar.xz
  md5 fc206ce1fca9cbd4f7493c81a2f2d2fb
- Build only the x86_64 system emulator with the book's options
  (--disable-download, --disable-pa, --audio-drv-list=alsa,
  --enable-slirp); qemu-img, qemu-io, qemu-nbd, qemu-storage-daemon and
  the guest tools are still installed.
- New dependency chain from the book: dtc 1.8.1 (libfdt) and libslirp
  4.9.7, both built and published for this.
- The bridge helper is installed setuid root with group kvm, as the book
  does, so unprivileged users in the kvm group can use -netdev bridge.
