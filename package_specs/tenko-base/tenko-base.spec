Name:       tenko-base
Version:    13.1
Release:    12
# Tenko rename compatibility (issue #22).
Obsoletes: browneye-base < 13.1-12
Provides: browneye-base = %{version}-%{release}
Summary:    Tenko Linux base system
License:    MIT
Prefix:     /usr

%include %{_sourcedir}/devel-obsoletes.inc

# BEGIN GENERATED REQUIRES: generated from tenko.lock + requires-extra
# Run scripts/gen_base_requires.py after changing either file.
Requires:   man-pages
Requires:   iana-etc
Requires:   glibc
Requires:   zlib
Requires:   bzip2
Requires:   xz
Requires:   lz4
Requires:   zstd
Requires:   file
Requires:   readline
Requires:   pcre2
Requires:   m4
Requires:   bc
Requires:   flex
Requires:   tcl
Requires:   expect
Requires:   dejagnu
Requires:   ninja
Requires:   pkgconf
Requires:   binutils
Requires:   gmp
Requires:   mpfr
Requires:   mpc
Requires:   attr
Requires:   acl
Requires:   libcap
Requires:   libxcrypt
Requires:   shadow
Requires:   gawk
Requires:   gcc
Requires:   ncurses
Requires:   sed
Requires:   psmisc
Requires:   gettext
Requires:   bison
Requires:   grep
Requires:   bash
Requires:   libtool
Requires:   gdbm
Requires:   gperf
Requires:   expat
Requires:   inetutils
Requires:   less
Requires:   perl
Requires:   autoconf
Requires:   automake
Requires:   openssl
Requires:   elfutils
Requires:   libffi
Requires:   sqlite
Requires:   mpdecimal
Requires:   python
Requires:   python-flit-core
Requires:   python-packaging
Requires:   python-wheel
Requires:   python-setuptools
Requires:   meson
Requires:   kmod
Requires:   coreutils
Requires:   diffutils
Requires:   findutils
Requires:   groff
Requires:   gzip
Requires:   iproute2
Requires:   kbd
Requires:   libpipeline
Requires:   make
Requires:   patch
Requires:   tar
Requires:   texinfo
Requires:   vim-minimal
Requires:   python-markupsafe
Requires:   python-jinja
Requires:   systemd
Requires:   dbus-daemon
Requires:   dbus-libs
Requires:   man-db
Requires:   procps-ng
Requires:   util-linux
Requires:   e2fsprogs
Requires:   tenko-rpm-config
Requires:   tenko-basefs
Requires:   tenko-sysconfig
Requires:   tenko-release
Requires:   tenko-firstboot
Requires:   glibc-locales
Requires:   gcc-lto
Requires:   linux-api-headers
Requires:   linux-pam
Requires:   make-ca
Requires:   libtirpc
Requires:   libseccomp
Requires:   libbsd
Requires:   libmd
Requires:   rpm
Requires:   popt
Requires:   libarchive
Requires:   lua
Requires:   openssh
Requires:   git
# END GENERATED REQUIRES

%description
Meta-package pulling in the Tenko base system.

%prep

%build

%install

%files

%changelog
* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-12
- Rename browneye-base to tenko-base and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Fri Nov 06 2026 browneye <build@browneye.invalid> 13.1-11
- Add openssh and git to the base meta (via requires-extra).  Both specs
  are already at the base-set versions (OpenSSH 10.6p1, git 2.56.0).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 13.1-10
- Expand the Obsoletes list to all 147 -devel packages the distro has
  ever shipped, not just the 99 left in the 2026-11-05 repository.
  Installed systems can still carry older versions: the build host had
  libgpg-error-devel, libidn2-devel and libxau-devel from earlier
  snapshots, and the unversioned Obsoletes makes their upgrade resolve
  cleanly too (issue #4).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 13.1-9
- Obsolete the 99 -devel packages that were folded into their runtime
  packages.  Without the Obsoletes an installed glib-devel (for example)
  requires glib = <old release> and blocks upgrading glib, so a build
  system cannot move to the new layout.  The version bound keeps a newer
  third-party -devel package from being removed (issue #4).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 13.1-8
- Drop the glibc-devel, gcc-devel and openssl-devel requirements: those
  subpackages are gone and their headers, linker scripts and .pc files
  now ship in glibc, gcc and openssl (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 13.1-7
- Require make-ca so installed systems and derived images get a CA trust
  store automatically.  This pulls p11-kit and libtasn1 and provides
  /etc/pki/tls/certs/ca-bundle.crt plus the /etc/ssl/certs links used by
  curl, git and OpenSSL consumers.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-6
- Require vim-minimal instead of the vim meta package: the runtime base
  does not need vim-runtime-extra (documentation, spell, tutor,
  translations, ~27 MB).  Installing vim still pulls the full set

* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-5
- Require gcc-devel and gcc-lto: the build image disables weak deps, and
  gcc alone no longer carries headers/static libs/LTO after the
  toolchain split

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
- Base meta-package
