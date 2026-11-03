Name:       libslirp
Version:    4.9.7
Release:    1
Summary:    User-mode networking library for virtual machines
License:    BSD-3-Clause
URL:        https://gitlab.freedesktop.org/slirp/libslirp
Source0:    %{name}-v%{version}.tar.bz2
Prefix:     /usr

%description
libslirp is a general-purpose user-mode networking stack used by virtual
machine emulators such as qemu.  It implements a virtual NAT network
entirely in userspace, so guests get DHCP, DNS, TCP and UDP without any
host configuration or elevated privileges.  qemu's `-nic user` uses it.

libslirp-4.9.7 is the version in BLFS r13.1 (networking/netlibs/libslirp).

%prep
%setup -q -n %{name}-v%{version}

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

%files -f %{_sourcedir}/libslirp.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 4.9.7-1
- New package for the qemu dependency chain.  libslirp is in BLFS r13.1
  at 4.9.7.
- Source: https://gitlab.freedesktop.org/slirp/libslirp/-/archive/v4.9.7/libslirp-v4.9.7.tar.bz2
  md5 e0463720a453b4221588c08878f759eb
- Built with meson --buildtype=release as the book does; qemu 11.1.3 is
  configured with --enable-slirp so user-mode networking (and the
  hostfwd used by the desktop test) works without root.
