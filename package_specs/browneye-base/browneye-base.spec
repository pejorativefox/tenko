Name:       browneye-base
Version:    13.1
Release:    4
Summary:    Browneye Linux base system (LFS r13.1)
License:    MIT
Prefix:     /usr

Requires: man-pages
Requires: iana-etc
Requires: glibc
Requires: glibc-devel
Requires: glibc-locales
Requires: zlib
Requires: bzip2
Requires: xz
Requires: lz4
Requires: zstd
Requires: file
Requires: readline
Requires: pcre2
Requires: m4
Requires: bc
Requires: flex
Requires: tcl
Requires: expect
Requires: dejagnu
Requires: ninja
Requires: pkgconf
Requires: binutils
Requires: gmp
Requires: mpfr
Requires: mpc
Requires: attr
Requires: acl
Requires: libcap
Requires: libxcrypt
Requires: shadow
Requires: gawk
Requires: gcc
Requires: ncurses
Requires: sed
Requires: psmisc
Requires: gettext
Requires: bison
Requires: grep
Requires: bash
Requires: libtool
Requires: gdbm
Requires: gperf
Requires: expat
Requires: inetutils
Requires: less
Requires: perl
Requires: autoconf
Requires: automake
Requires: openssl
Requires: openssl-devel
Requires: elfutils
Requires: libffi
Requires: sqlite
Requires: mpdecimal
Requires: python
Requires: python-flit-core
Requires: python-packaging
Requires: python-wheel
Requires: python-setuptools
Requires: meson
Requires: kmod
Requires: coreutils
Requires: diffutils
Requires: findutils
Requires: groff
Requires: gzip
Requires: iproute2
Requires: libtirpc
Requires: kbd
Requires: libpipeline
Requires: make
Requires: patch
Requires: tar
Requires: texinfo
Requires: vim
Requires: python-markupsafe
Requires: python-jinja
Requires: systemd
Requires: dbus-daemon
Requires: dbus-libs
Requires: man-db
Requires: procps-ng
Requires: util-linux
Requires: e2fsprogs
Requires: libseccomp
Requires: libbsd
Requires: libmd
Requires: linux-api-headers
Requires: rpm
Requires: popt
Requires: libarchive
Requires: lua
Requires: browneye-rpm-config
Requires: browneye-basefs
Requires: browneye-sysconfig
Requires: browneye-release
Requires: browneye-firstboot
Requires: linux-pam

%description
Meta-package pulling in the LFS r13.1 base system.

%prep

%build

%install

%files

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-4
- Require glibc-devel and openssl-devel so the base build image keeps the
  headers/crt/linker scripts after the glibc and openssl splits
  (size audit §7)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-3
- Require libtirpc for iproute2 (size audit P0)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-2
- Require linux-pam (systemd is PAM-enabled) and browneye-firstboot
  (root password policy, E5)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 13.1
- LFS r13.1 base meta-package
