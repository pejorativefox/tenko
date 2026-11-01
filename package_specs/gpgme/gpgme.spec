Name:       gpgme
Version:    2.2.0
Release:    1
Summary:    High-level crypto API for GnuPG
License:    LGPL
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

%description
GPGME is a library that allows applications to access GnuPG functionality
without requiring knowledge of the GnuPG internals.

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

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.2.0-1
- Update to the BLFS r13.1 version (2.2.0, was 1.21.0) for the E1
  dnf/libdnf dependency chain.
- Built with --disable-static --disable-gpg-test (no gnupg binary in the
  build image; the Browneye repo is unsigned, so signature helpers are not
  exercised at assembly time).
- Use a generated static filelist.
