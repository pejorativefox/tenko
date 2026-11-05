Name:       libassuan
Version:    3.0.2
Release:    6
Summary:    IPC library used by GnuPG and related components
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.bz2

%description
libassuan is the IPC library used by GnuPG, gpgme and the dnf/librepo
dependency chain.  It depends on libgpg-error.

%prep
%setup -q

%build
%configure --prefix=/usr --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libassuan.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.0.2-6
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 3.0.2-5
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.0.2-3
- Move the pkg-config files into a new -devel subpackage so the runtime
  package no longer drags pkgconfig(...) consumers into every install.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.0.2-2
- Bump the release: -1 was already published with different content, and
  re-publishing the same NEVRA would leave the repo metadata stale.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.0.2-1
- New package (BLFS r13.1): required by gpgme, which librepo uses for
  repository signature handling.
