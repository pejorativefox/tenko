Name:       libassuan
Version:    3.0.2
Release:    2
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
* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.0.2-2
- Bump the release: -1 was already published with different content, and
  re-publishing the same NEVRA would leave the repo metadata stale.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.0.2-1
- New package (BLFS r13.1): required by gpgme, which librepo uses for
  repository signature handling.
