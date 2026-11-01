Name:       browneye-build
Version:    13.1
Release:    1
Summary:    Browneye build and repository assembly tools
License:    MIT
Prefix:     /usr

Requires:   dnf = 4.24.0
Requires:   createrepo_c = 1.2.6

%description
Meta-package for the tools needed to build Browneye RPMs and to assemble
and install the Browneye repository inside the self-hosted build image.

This is deliberately separate from browneye-base and xfce-desktop: dnf and
createrepo_c are build/assembly tools, not part of the minimal base or
desktop systems.  Install this package in an image that also carries the
base toolchain.

%files

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-1
- New meta-package for the self-hosted repo/rootfs assembly toolchain
  (E1).  Requires dnf and createrepo_c only; their dependency chains
  (libdnf, libsolv, libcomps, libmodulemd, librepo, zchunk, glib,
  libxml2, curl, gpgme, swig, ...) are pulled in by RPM requires.
