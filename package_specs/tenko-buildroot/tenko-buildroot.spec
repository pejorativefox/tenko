Name:       tenko-buildroot
Version:    6
Release:    1
Epoch:      1
Summary:    Tenko Linux minimal RPM buildroot (toolchain baseline)
License:    MIT
Prefix:     /usr

# The toolchain baseline every package build starts from (issue #58).
# Anything else a build needs must be declared as BuildRequires in its
# spec; `tenko build` with STRICT=1 builds in an image holding only this
# package and verifies exactly that.  Removing an entry is a policy change:
# specs that relied on it implicitly must declare it first.

# Core utilities rpmbuild and its scriptlets use.
Requires:   tenko-basefs
Requires:   bash
Requires:   coreutils
Requires:   sed
Requires:   grep
Requires:   gawk
Requires:   findutils
Requires:   tar
Requires:   gzip
Requires:   xz
Requires:   bzip2
Requires:   cpio
Requires:   diffutils
Requires:   file
Requires:   which
Requires:   util-linux
# C.UTF-8: build images set LANG=C.UTF-8.
Requires:   glibc-locales

# RPM tooling and the Tenko macros.
Requires:   rpm
Requires:   tenko-rpm-config

# Toolchain.
Requires:   gcc
Requires:   binutils
Requires:   make
Requires:   patch
Requires:   pkgconf
Requires:   m4
Requires:   autoconf
Requires:   automake
Requires:   libtool
Requires:   bison
Requires:   flex
Requires:   gettext
Requires:   meson
Requires:   ninja
Requires:   cmake
Requires:   linux-api-headers
Requires:   python

# The builder installs BuildRequires from inside the build container, and
# `tenko build` maintains the local repository with createrepo_c.  These
# replace tenko-build (no exact version pins).
Requires:   dnf
Requires:   createrepo_c
Obsoletes:  tenko-build < 1:6-2
Provides:   tenko-build = 1:6-2

%description
The minimal Tenko RPM buildroot: core utilities, rpm with the Tenko macros,
the GCC toolchain, autotools, gettext, meson/ninja/cmake, kernel headers,
Python, and dnf/createrepo_c for installing build dependencies.  A package
build gets this plus the BuildRequires its spec declares, and nothing else.

tenko-base-build layers the runtime base and common development extras on
top of it for interactive development hosts.

%files

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 6-1
- New toolchain-baseline meta for strict builds (issue #58).  Absorbs
  tenko-build (dnf, createrepo_c) without its exact version pins.
