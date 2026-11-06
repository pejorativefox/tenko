# Source0: https://github.com/lfs-book/make-ca/archive/v1.16.1/make-ca-1.16.1.tar.gz
#   md5 bf9cea2d24fc5344d4951b49f275c595
# Source1: https://hg-edge.mozilla.org/releases/mozilla-release/raw-file/default/security/nss/lib/ckfw/builtins/certdata.txt
#   raw snapshot 2026-11-01: md5 e66a4b50d8cc441b2a10f185310c7901
#   sha256 beb7e6dfe6499926e52c075c27bcfbe4c957f8609c575b3860273ae2806f63eb
#   shipped file adds "# Revision:20261101" for deterministic make-ca output:
#   md5 4900ad4c4b7189533000eaeb30f62cc6
#   sha256 fe159c29bbf50b3f0a8e60396e6a534efef1f4c349fda2436675530ce810ea98
#
# make-ca normally downloads certdata.txt; the snapshot is shipped as a
# source so the package builds and regenerates its trust store offline.
Name:       make-ca
Version:    1.16.1
Release:    3
Summary:    PKI setup script and Mozilla CA trust store
License:    GPL-3.0-or-later
URL:        https://github.com/lfs-book/make-ca
Source0:    %{name}-%{version}.tar.gz
Source1:    certdata.txt
Prefix:     /usr

Requires:   p11-kit
Requires:   openssl
Requires:   coreutils
Requires:   gawk
Requires:   grep
Requires:   sed
BuildRequires: p11-kit
BuildRequires: openssl
Provides:   ca-certificates = %{version}-%{release}

%description
make-ca is a utility to deliver and manage a complete PKI configuration
using standard GNU utilities, OpenSSL and p11-kit.  This package also ships
a pinned Mozilla certdata.txt snapshot and the CA trust stores generated
from it, so the system works offline.

The package owns the p11-kit anchors, the OpenSSL hashed certificate
directory, the GnuTLS bundles, and the conventional
/etc/pki/tls/certs/ca-bundle.crt path used by curl and git.

%prep
%setup -q
sed '/mktemp/s/-t //' -i make-ca

# make-ca recreates CERTDIR on every run (including update-ca-certificates);
# keep the conventional curl/git bundle names afterwards.
cat >> make-ca << "TENKOCA"
# Tenko: expose the GnuTLS bundle under the conventional names.
if [ -e "${DESTDIR}${CABUNDLE}" ]; then
    ln -sf /etc/pki/tls/certs/ca-bundle.crt "${DESTDIR}${CERTDIR}/ca-bundle.crt"
    ln -sf /etc/pki/tls/certs/ca-bundle.crt "${DESTDIR}${CERTDIR}/ca-certificates.crt"
fi
TENKOCA

%build
make

%install
rm -rf %{buildroot}
%make_install

install -d %{buildroot}/etc/pki %{buildroot}/etc/ssl

# make-ca generates the anchors under DESTDIR, but p11-kit's trust module
# reads its input paths at compile time.  Point the installed module config at
# the buildroot anchors so the network-free generation is self-contained.
# The backup must live outside /usr/share/p11-kit/modules: p11-kit loads every
# file in that directory.
MOD=/usr/share/p11-kit/modules/p11-kit-trust.module
cp -a "$MOD" /tmp/p11-kit-trust.module.tenko-build
sed -i "s|^x-init-reserved:.*|x-init-reserved: paths=%{buildroot}/etc/pki/anchors|" "$MOD"
%{buildroot}/usr/sbin/make-ca -D %{buildroot} -f -C %{SOURCE1} \
    > %{_builddir}/make-ca-generate.log 2>&1
mv -f /tmp/p11-kit-trust.module.tenko-build "$MOD"

# Conventional names used by curl, git and OpenSSL consumers.
ln -sf /etc/pki/tls/certs/ca-bundle.crt %{buildroot}/etc/ssl/certs/ca-bundle.crt
ln -sf /etc/pki/tls/certs/ca-bundle.crt %{buildroot}/etc/ssl/certs/ca-certificates.crt

# Fail the build if the generated server-auth bundle is unusable.
test "$(grep -c 'BEGIN CERTIFICATE' %{buildroot}/etc/pki/tls/certs/ca-bundle.crt)" -gt 0
grep -q 'ISRG Root X1' %{buildroot}/etc/pki/tls/certs/ca-bundle.crt

%post
# The package ships a trust bundle that %install generated and verified.
# Only regenerate it when it is missing: in a restricted installroot (no
# /dev, early boot) make-ca cannot read the anchors and would silently
# replace the bundle with an empty file, which breaks HTTPS for dnf.
if [ ! -s /etc/pki/tls/certs/ca-bundle.crt ] &&
   [ -x /usr/sbin/make-ca ] && [ -r /etc/ssl/certdata.txt ]; then
    /usr/sbin/make-ca -f -C /etc/ssl/certdata.txt >/dev/null 2>&1 || :
fi
# make-ca recreates /etc/ssl/certs; restore the curl/git bundle names.
mkdir -p /etc/ssl/certs
if [ -e /etc/pki/tls/certs/ca-bundle.crt ]; then
    ln -sf /etc/pki/tls/certs/ca-bundle.crt /etc/ssl/certs/ca-bundle.crt
    ln -sf /etc/pki/tls/certs/ca-bundle.crt /etc/ssl/certs/ca-certificates.crt
fi

%files -f %{_sourcedir}/make-ca.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.16.1-3
- %post only regenerates the trust bundle when it is missing.  In a
  restricted installroot make-ca cannot read the anchors and wrote an
  empty bundle, so the live ISO had no CA certificates and HTTPS to the
  package repository would fail.  The package already ships a populated,
  build-verified bundle.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.16.1-2
- Stop owning %dir /etc/ssl/certs: make-ca created it 0555 while
  openssl-libs ships it 0755, so installing both aborted the dnf
  transaction with a directory-mode file conflict.  openssl-libs owns
  the directory; make-ca only ships the hashed certs and bundle links

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.16.1-1
- Update to 1.16.1 (BLFS r13.1)
- Ship a pinned Mozilla certdata.txt snapshot and generate the trust store
  offline during %install; %post regenerates it without network
- Provide ca-certificates and the curl/OpenSSL CA bundle paths
- Replace the directory listing with a generated static filelist
