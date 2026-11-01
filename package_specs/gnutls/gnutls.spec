Name:       gnutls
Version:    3.8.13
Release:    1
Summary:    A TLS protocol implementation
License:    LGPL-2.1-or-later AND GPL-3.0-or-later
URL:        https://www.gnutls.org/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: nettle
BuildRequires: gmp
BuildRequires: libtasn1
BuildRequires: p11-kit

# Runtime TLS primitives.  The shared-library sonames are generated
# automatically; this keeps the package name visible to dependency tools.
Requires:      nettle

%description
GnuTLS is a secure layer over a reliable transport layer.  It implements
the TLS 1.3, TLS 1.2, TLS 1.1 and TLS 1.0 protocols along with X.509, OpenPGP
and PSK authentication, and ships the gnutls-cli/certtool/p11tool utilities.

The package bundles libunistring (--with-included-unistring) because
libunistring is not part of the Browneye package set; this mirrors the
historical GnuTLS spec and avoids an unpackaged runtime dependency.

%prep
%setup -q

%build
%configure                       \
    --prefix=/usr                \
    --docdir=%{_docdir}/%{name}-%{version} \
    --with-default-trust-store-pkcs11="pkcs11:" \
    --with-included-unistring
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -rf %{buildroot}%{_infodir}/dir

%files -f %{_sourcedir}/gnutls.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 3.8.13
- Update to 3.8.13 (BLFS r13.1)
- Build against nettle 4.0, libtasn1 4.21.0 and p11-kit 0.26.5
- Use the PKCS#11 trust store and the bundled libunistring
- Replace the hand-written file list with a generated static filelist

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 3.5.19
- Initial RPM
