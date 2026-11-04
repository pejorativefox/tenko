Name:       passt
Version:    2026_10_02.cba3570
Release:    1
Summary:    User-mode networking daemons for virtual machines and namespaces
License:    GPL-2.0-or-later AND BSD-3-Clause
URL:        https://passt.top/
Source0:    passt-cba357068dc586e7540971eb40bb56c5e62c4de1.tar.xz
Prefix:     /usr
# The avx2 binaries and the file list are x86_64-specific.
ExclusiveArch: x86_64

%description
passt implements a translation layer between a Layer-2 network interface and
native Layer-4 sockets (TCP, UDP, ICMP/ICMPv6 echo) on a host.  It does not
require capabilities or privileges and can replace Slirp for QEMU.

pasta, built from the same binary, provides equivalent functionality for
network namespaces: traffic is forwarded through a tap interface inside the
namespace without creating further interfaces on the host.  It is the default
rootless network backend for podman.

%package -n pasta
Summary:    User-mode networking for network namespaces
Requires:   passt = %{version}-%{release}
License:    GPL-2.0-or-later AND BSD-3-Clause

%description -n pasta
pasta (Pack A Subtle Tap Abstraction) forwards traffic from a network namespace
through a tap interface using native Layer-4 sockets on the host.  It is the
default rootless network backend for podman.

%prep
%setup -q -n passt-cba357068dc586e7540971eb40bb56c5e62c4de1

%build
%make_build VERSION=%{version}

%install
rm -rf %{buildroot}
%make_install \
    prefix=%{_prefix} \
    bindir=%{_bindir} \
    mandir=%{_mandir} \
    docdir=%{_docdir}/%{name}

%files -f %{_sourcedir}/passt.filelist

%files -n pasta -f %{_sourcedir}/pasta.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 2026_10_02.cba3570-1
- New package: upstream passt tag 2026_10_02.cba3570 (commit cba3570).
  This is the same passt/pasta release bundled by podman-bin 6.1.4 and the
  version Fedora 44 ships.  passt/pasta are not in LFS or BLFS r13.1; the
  user approved this upstream source as the version-parity exception.
- Source: https://passt.top/passt/snapshot/passt-cba357068dc586e7540971eb40bb56c5e62c4de1.tar.xz
  md5 61101a96a411d3451d770786baa6e99e
  sha256 2bd6f52562a201e8960c17d6ae459a10bb18dc7ef2e7fa617ec82a872db9e403
  sha512 c35cdc6d587a6fa00b1b55aa0f8d1da3bc628d457d25dc8cf49e15118cf5cac53b71c4098da5c65e19aa1b80531cbdd25684773e0f2d99d39a55cbc6d55cdb6e
- Build with make VERSION=%{version}; install passt, passt.avx2,
  passt-repair and pesto in passt, and the pasta/pasta.avx2 symlinks plus
  their man pages in the separate pasta package.
