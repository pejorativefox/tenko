Name:       tenko-build
Version:    13.1
Release:    2
# Tenko rename compatibility (issue #22).
Obsoletes: browneye-build < 13.1-2
Provides: browneye-build = %{version}-%{release}
Summary:    Tenko build and repository assembly tools
License:    MIT
Prefix:     /usr

Requires:   dnf = 4.24.0
Requires:   createrepo_c = 1.2.6

%description
Meta-package for the tools needed to build Tenko RPMs and to assemble
and install the Tenko repository inside the self-hosted build image.

This is deliberately separate from tenko-base and xfce-desktop: dnf and
createrepo_c are build/assembly tools, not part of the minimal base or
desktop systems.  Install this package in an image that also carries the
base toolchain.

%files

%changelog
* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-2
- Rename browneye-build to tenko-build and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 13.1-1
- New meta-package for the self-hosted repo/rootfs assembly toolchain
  (E1).  Requires dnf and createrepo_c only; their dependency chains
  (libdnf, libsolv, libcomps, libmodulemd, librepo, zchunk, glib,
  libxml2, curl, gpgme, swig, ...) are pulled in by RPM requires.
