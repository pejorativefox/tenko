Name:       browneye-base-runtime
Version:    13.1
Release:    6
Summary:    Browneye Linux runtime base (no build toolchain)
License:    MIT
Prefix:     /usr

# The LFS r13.1 base system without the compiler/toolchain, development
# headers, static libraries, documentation toolchain or Python build
# backends.  browneye-base itself is unchanged and remains the LFS
# build-capable meta.
Requires:   iana-etc
Requires:   glibc
Requires:   glibc-locales
Requires:   gcc-libs
Requires:   zlib
Requires:   bzip2
Requires:   xz
Requires:   lz4
Requires:   zstd
Requires:   file
Requires:   readline
Requires:   pcre2
Requires:   attr
Requires:   acl
Requires:   libcap
Requires:   libxcrypt
Requires:   shadow
Requires:   gawk
Requires:   ncurses
Requires:   sed
Requires:   psmisc
Requires:   gettext-libs
Requires:   grep
Requires:   bash
Requires:   gdbm
Requires:   expat
Requires:   inetutils
Requires:   less
Requires:   perl
Requires:   openssl
Requires:   elfutils
Requires:   libffi
Requires:   sqlite
Requires:   mpdecimal
Requires:   python
Requires:   kmod
Requires:   coreutils
Requires:   diffutils
Requires:   findutils
Requires:   gzip
Requires:   iproute2
Requires:   libtirpc
Requires:   kbd
Requires:   libpipeline
Requires:   tar
Requires:   vim-minimal
Requires:   systemd
Requires:   dbus-daemon
Requires:   dbus-libs
Requires:   procps-ng
Requires:   util-linux
Requires:   e2fsprogs
Requires:   libseccomp
Requires:   libbsd
Requires:   libmd
Requires:   rpm
Requires:   popt
Requires:   libarchive
Requires:   lua
Requires:   browneye-basefs
Requires:   browneye-sysconfig
Requires:   browneye-release
Requires:   browneye-firstboot
Requires:   linux-pam
Requires:   make-ca
Requires:   openssh
Requires:   git

%description
The Browneye Linux base system with no build toolchain: libc and the
runtime libraries, the shell and core utilities, systemd/udev, D-Bus,
the RPM runtime, Python and Perl runtimes, OpenSSH and git, and the
Browneye system configuration packages.

This profile deliberately omits gcc/gcc-lto, binutils,
linux-api-headers, the autotools (m4, autoconf, automake, libtool,
bison, flex, gperf), gettext-tools, texinfo, meson/ninja/pkgconf,
Python build backends (setuptools, wheel, flit-core, packaging, jinja,
markupsafe), man-db, man-pages, groff and the documentation/translation
subpackages.  Development headers and .pc files ship in the runtime
packages themselves, so installing a library also provides what is
needed to compile against it.  It is the base for a runtime container,
appliance or a desktop installed over browneye-base-runtime instead of
browneye-base.

Installing browneye-base is still the supported way to get an LFS
build-capable system.

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/browneye
touch %{buildroot}/usr/share/browneye/base-runtime

%files
/usr/share/browneye/base-runtime

%changelog
* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-6
- Restore the openssh/git requires.  The installer pulls
  browneye-base-runtime from the network repository, so this gives existing
  installer media the tools without an ISO rebuild.  build_iso_uefi.sh now
  masks sshd and sshd-keygen in the live root so the debugging root password
  is never exposed over the network.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-5
- Revert the openssh/git requires from 13.1-4.  browneye-base-runtime is
  also the live ISO base, and the live media must not start sshd with the
  debugging root password.  The tools are in browneye-base and the
  installer target package set instead.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-4
- Require openssh and git so every installed base system (desktop or
  base-only) has the SSH client/server and Git.  Both specs are already at
  the BLFS r13.1 versions (OpenSSH 10.6p1, git 2.56.0).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 13.1-3
- Note that development headers and .pc files now ship in the runtime
  packages, after the -devel subpackages were removed (issue #4).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 13.1-2
- Require make-ca.  browneye-base had it, but the runtime meta (used by the
  live installer and by network installs) did not, so neither the live
  environment nor a freshly installed system had a CA trust store.  That
  breaks HTTPS for dnf now that installs pull from the repository URL.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-1
- New runtime-only base profile: browneye-base without the compiler,
  autotools, devel/static subpackages, documentation toolchain or Python
  build backends (size audit B3)
