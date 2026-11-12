Name:       tenko-base
Version:    6
Release:    13
Epoch:      1
Summary:    Tenko Linux base system
License:    MIT
URL:        https://github.com/pejorativefox/tenko
Prefix:     /usr

%include %{_sourcedir}/devel-obsoletes.inc

# Layering: the base system is the installed runtime plus the development
# environment, then the base package set below.
Requires:   tenko-base-runtime
Requires:   tenko-base-build

# BEGIN GENERATED REQUIRES: generated from package_specs/base.json + requires-extra
# Run ./tenko base-requires after changing either file.
Requires:   man-pages
Requires:   iana-etc
Requires:   glibc
Requires:   zlib
Requires:   bzip2
Requires:   xz
Requires:   lz4
Requires:   zstd
Requires:   zip
Requires:   unzip
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
Requires:   bash-completion
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
Requires:   font-dejavu-sans-mono
Requires:   font-noto-cjk
Requires:   font-noto-emoji
Requires:   font-nerd-symbols
Requires:   font-ttf-unifont
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
Requires:   lsof
Requires:   strace
Requires:   nano
Requires:   libblockdev
Requires:   udisks2
Requires:   fwupd
Requires:   tuned
Requires:   tenko-rpm-config
Requires:   tenko-basefs
Requires:   tenko-sysconfig
Requires:   tenko-release
Requires:   tenko-firstboot
Requires:   tenko-suspend-log
Requires:   glibc-locales
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
Requires:   curl
Requires:   wget
Requires:   rsync
Requires:   pciutils
Requires:   usbutils
Requires:   which
Requires:   ncdu
Requires:   htop
Requires:   bwm-ng
Requires:   NetworkManager
Requires:   wpa-supplicant
Requires:   nmtui
Requires:   linux-firmware-base
Requires:   libtsm
Requires:   kmscon
# END GENERATED REQUIRES

%description
Meta-package pulling in the Tenko base system.

%prep

%build

%install

%files

%changelog
* Thu Nov 12 2026 tenko <build@tenko.invalid> 6-13
- Stop requiring gcc-lto: gcc carries the LTO backend and linker plugin
  again, so gcc alone links Rust and -flto (issue #63).

* Wed Nov 11 2026 tenko <build@tenko.invalid> 6-12
- Require tenko-base-runtime and tenko-base-build, so the base system is
  a strict superset of both instead of a separate flat list (it was
  missing gcc-libs and gettext-libs from the runtime set).
- Move nodejs, podman-bin and ncat out of the base: they belong to the
  developer profiles (tenko-workstation and tenko-osdev already carry
  nodejs/podman-bin; tenko-osdev now carries ncat).  Existing installs keep
  them until removed; `dnf autoremove` may offer to drop them.

* Wed Nov 11 2026 tenko <build@tenko.invalid> 6-11
- Promote font-ttf-unifont into the base package set (packages and rebuild
  order).  Its fontconfig snippet is the final monospace fallback and covers
  the leftover BMP characters (U+2B1D, U+23F5) that still rendered as tofu
  after DejaVu Sans Mono fixed the Dingbats and Geometric Shapes ranges.

* Wed Nov 11 2026 tenko <build@tenko.invalid> 6-10
- Promote font-dejavu-sans-mono into the base package set (packages and
  rebuild order).  DejaVu Sans Mono covers the Dingbats, Miscellaneous
  Symbols and Geometric Shapes characters that Terminus, Noto CJK, Noto Emoji
  and Symbols Nerd Font Mono lack, so TUIs no longer render them as tofu or
  as double-width CJK glyphs.

* Tue Nov 10 2026 tenko <build@tenko.invalid> 6-9
- Require tenko-suspend-log so every base install records suspend/resume
  cycles.  A lid-suspend test that failed to bring the desktop back on the
  first resume could only be reconstructed from raw kernel messages; the new
  package logs the cycle, the wakeup source and the post-resume X state, and
  ships tenko-suspend-report for a bug report.

* Tue Nov 10 2026 tenko <build@tenko.invalid> 6-8
- Promote tuned into the base package set (packages and rebuild order),
  so every base install runs the dynamic system tuning daemon.  The
  runtime meta lists it too because the installer and live media install
  tenko-base-runtime instead of tenko-base.

* Tue Nov 10 2026 browneye <build@browneye.invalid> 6-7
- Promote zip and unzip into the base package set (packages and rebuild
  order) so every Tenko system can create and extract .zip archives, not
  just read them.  The RPMs were already published (zip 3.0-1, unzip
  6.0-1); base membership puts them on new installs and upgrades.

* Mon Nov 09 2026 browneye <build@browneye.invalid> 6-6
- Add the user-requested base console tools through requires-extra: curl,
  wget, rsync, pciutils, usbutils, which, htop, bwm-ng and ncdu.  They
  are base-install extras, not base.json rebuild-order members; htop and
  ncdu were already listed.

* Mon Nov 09 2026 browneye <build@browneye.invalid> 6-5
- Promote the storage, firmware and diagnostic packages into the base
  package set: libblockdev and udisks2 provide the block-device service
  and its backend, fwupd covers firmware updates, and lsof, strace and
  nano are the requested base diagnostics/editor tools.  base.json carries
  them in packages and build_order, so tenko-base and the base rebuild
  order both include them.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-4
- Add the console Unicode stack.  font-noto-cjk, font-noto-emoji and
  font-nerd-symbols are base packages (and in the rebuild order); libtsm
  and kmscon are runtime extras.  kmscon replaces fbcon on the VTs because
  the kernel console is capped at 512 glyphs and cannot render Simplified
  Chinese; the fonts give the desktop terminal Chinese, emoji and Nerd Font
  icon fallback.

* Sun Nov 08 2026 tenko <build@tenko.invalid> 6-3
- Move bash-completion from requires-extra into base.json, so it is part
  of the base package set and base rebuild order instead of an extra
  requirement.  The resolved base transaction is unchanged.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-2
- Add NetworkManager, wpa-supplicant and nmtui to the base install, plus
  linux-firmware-base for the signed regulatory database.  This makes
  wired and wireless networking available out of the box, with nmtui as
  the text UI.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-1
- Rebase on the Tenko 6 distro release with Epoch 1 so installs carrying
  the old 13.1 EVR upgrade cleanly.
- Drop the browneye-base Obsoletes/Provides alias; no Browneye installs
  remain.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 13.1-13
- Add ncat, ncdu, htop, nodejs, bash-completion and podman-bin to the base
  install (user-requested; podman-bin provides podman).

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
