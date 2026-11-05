Name:       libgpg-error
Version:    1.61
Release:    4
Summary:    Library of error codes and messages for GnuPG components
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

%description
libgpg-error provides the common error codes, messages and helper macros
shared by GnuPG, libgcrypt, libassuan and gpgme.  BLFS r13.1 version.

%prep
%setup -q

%build
%configure --prefix=/usr --sysconfdir=/etc --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
install -v -m644 -D README \
    %{buildroot}/usr/share/doc/libgpg-error-%{version}/README

%files -f %{_sourcedir}/libgpg-error.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.61-4
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.61-2
- Bump the release: -1 was already published with different content, and
  re-publishing the same NEVRA would leave the repo metadata stale.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.61-1
- New package (BLFS r13.1): build dependency of libassuan and gpgme, which
  are required for the libdnf/librepo dnf stack.
