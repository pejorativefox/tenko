Name:       gpgme
Version:    2.2.0
Release:    6
Summary:    High-level crypto API for GnuPG
License:    LGPL
Prefix:     /usr
Recommends: gnupg
Source0:    %{name}-%{version}.tar.bz2

%description
GPGME is a library that allows applications to access GnuPG functionality
without requiring knowledge of the GnuPG internals.

%package devel
Summary:    Development files for gpgme
Requires:   %{name} = %{version}-%{release}

%description devel
pkg-config files for gpgme, used to build software against it.

%prep
%setup -q

%build
%configure --disable-static --disable-gpg-test
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/gpgme.filelist
%files devel -f %{_sourcedir}/gpgme-devel.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 2.2.0-6
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 2.2.0-4
- Recommends: gnupg, matching BLFS.  gpgme looks up its OpenPGP and CMS
  engines at runtime; without gnupg they are reported as unavailable
  (file=/nonexistent) and gpgme_ctx_set_engine_info fails.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.2.0-3
- Move the pkg-config files into a new -devel subpackage so the runtime
  package no longer drags pkgconfig(...) consumers into every install.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.2.0-2
- Rebuild for Python 3.15 / the D9 dnf stack refresh (new NEVR so the
  rebuilt package supersedes the published -1).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.2.0-1
- Update to the BLFS r13.1 version (2.2.0, was 1.21.0) for the E1
  dnf/libdnf dependency chain.
- Built with --disable-static --disable-gpg-test (no gnupg binary in the
  build image; the Browneye repo is unsigned, so signature helpers are not
  exercised at assembly time).
- Use a generated static filelist.
