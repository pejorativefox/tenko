Name:       keyutils
Version:    1.6.3
Release:    1
Summary:    Linux kernel key management utilities and library
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
URL:        https://git.kernel.org/pub/scm/linux/kernel/git/dhowells/keyutils.git
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
keyutils is a set of utilities and a library for managing the Linux kernel
key retention facility.  The kernel keyrings store authentication keys,
cryptographic keys and other security data for filesystems, block devices and
services such as NFS and Kerberos.

%prep
%setup -q

%build
%make_build \
    CFLAGS="%{optflags}" \
    LIBDIR=%{_libdir} \
    USRLIBDIR=%{_libdir} \
    BINDIR=%{_bindir} \
    SBINDIR=/usr/sbin \
    INCLUDEDIR=%{_includedir} \
    ETCDIR=%{_sysconfdir} \
    SHAREDIR=%{_datadir}/keyutils \
    NO_ARLIB=1

%install
rm -rf %{buildroot}
make install \
    DESTDIR=%{buildroot} \
    LIBDIR=%{_libdir} \
    USRLIBDIR=%{_libdir} \
    BINDIR=%{_bindir} \
    SBINDIR=/usr/sbin \
    INCLUDEDIR=%{_includedir} \
    ETCDIR=%{_sysconfdir} \
    SHAREDIR=%{_datadir}/keyutils \
    NO_ARLIB=1

%files -f %{_sourcedir}/keyutils.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 1.6.3-1
- Initial package at the latest stable upstream release, 1.6.3.
- Verified the licence as GPL-2.0-or-later AND LGPL-2.1-or-later from
  LICENCE.GPL and LICENCE.LGPL.
- Built the upstream tarball from the Debian orig mirror because the
  kernel.org cgit snapshot endpoint returns HTTP 403 to the build host.
