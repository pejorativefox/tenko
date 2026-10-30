Name:       browneye-base
Version:    13.1
Release:    1
Summary:    Browneye Linux base system (LFS r13.1)
License:    MIT
Prefix:     /usr

%description
Meta-package pulling in the LFS r13.1 base system.

Requires: man-pages
Requires: iana-etc
Requires: glibc
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
Requires: browneye-basefs
Requires: browneye-sysconfig
Requires: browneye-release

%prep

%build

%install

%files

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 13.1
- LFS r13.1 base meta-package
