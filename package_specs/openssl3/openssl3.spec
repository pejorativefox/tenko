Name:       openssl3
Version:    3.5.9
Release:    1
Summary:    OpenSSL 3.5 libraries, installable alongside OpenSSL 4
License:    Apache-2.0
URL:        https://www.openssl.org/
Source0:    openssl-%{version}.tar.gz
Prefix:     /usr

BuildRequires: perl

%description
OpenSSL 3.5, installed in a versioned tree under /usr/lib64/openssl3.
It can be installed alongside the distribution's OpenSSL 4 packages: the
two majors use different sonames (libssl.so.3/libcrypto.so.3 versus
libssl.so.4/libcrypto.so.4), and the headers, pkg-config files, command
and configuration of this copy live under the versioned prefix.

Install it when software built against the OpenSSL 3 ABI has to run or be
compiled on Tenko 6, for example an older Python interpreter built by
pyenv.  Point such builds at the tree with
--with-openssl=/usr/lib64/openssl3 (CPython) or
PKG_CONFIG_PATH=/usr/lib64/openssl3/lib/pkgconfig; Python interpreters
should also use --with-openssl-rpath=auto or the tree's ld.so.conf entry.
The tree provides the system CA bundle through /usr/lib64/openssl3/ssl.

%prep
%setup -q -n openssl-%{version}

%build
./Configure --prefix=%{_libdir}/openssl3     \
            --libdir=lib                     \
            --openssldir=%{_libdir}/openssl3/ssl \
            shared                           \
            zlib-dynamic                     \
            no-tests
%make_build

%install
rm -rf %{buildroot}
sed -i '/INSTALL_LIBS/s/libcrypto.a libssl.a//' Makefile
%make_install MANSUFFIX=ssl
rm -vf %{buildroot}%{_infodir}/dir*
rm -rf %{buildroot}%{_libdir}/openssl3/share/doc/openssl
rm -rf %{buildroot}%{_libdir}/openssl3/share/man
rm -f %{buildroot}%{_libdir}/openssl3/lib/*.a
# ssl/misc holds the CA management scripts.  tsget needs WWW::Curl::Easy,
# which the distribution does not provide; this copy is a runtime library,
# so ship neither the scripts nor the Perl requirements they generate.
rm -rf %{buildroot}%{_libdir}/openssl3/ssl/misc

# The whole tree is private, so nothing here collides with the OpenSSL 4
# packages except the command and loader configuration, which are versioned.
mkdir -p %{buildroot}%{_bindir}
ln -s ../lib64/openssl3/bin/openssl %{buildroot}%{_bindir}/openssl3

# An OpenSSL openssldir defaults to <openssldir>/cert.pem and <openssldir>/certs.
# Point them at the system CA store so this copy verifies certificates without
# the application setting SSL_CERT_FILE or SSL_CERT_DIR.
ln -sfn /etc/pki/tls/certs/ca-bundle.crt %{buildroot}%{_libdir}/openssl3/ssl/cert.pem
rm -rf %{buildroot}%{_libdir}/openssl3/ssl/certs
ln -sfn /etc/ssl/certs %{buildroot}%{_libdir}/openssl3/ssl/certs

# The libraries live in a versioned tree, so the loader needs the directory in
# its cache: otherwise libssl.so.3 is only found by callers that set an rpath
# or LD_LIBRARY_PATH.
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo %{_libdir}/openssl3/lib > %{buildroot}%{_sysconfdir}/ld.so.conf.d/openssl3.conf

%post
if [ -x /usr/sbin/ldconfig ]; then
    /usr/sbin/ldconfig
fi

%postun
if [ -x /usr/sbin/ldconfig ]; then
    /usr/sbin/ldconfig
fi

%files -f %{_sourcedir}/openssl3.filelist

%changelog
* Tue Nov 17 2026 tenko <build@tenko.invalid> 3.5.9-1
- New package, not in the base set: OpenSSL 3.5.9, the latest release on
  the 3.5 LTS branch (checked 2026-11-17), installed under
  /usr/lib64/openssl3 so it can coexist with the OpenSSL 4 packages that
  the distribution moved to.  It supplies the libssl.so.3/libcrypto.so.3
  ABI for software built against OpenSSL 3, such as older pyenv-built
  Python interpreters, and does not change the system openssl.  The
  tree carries the libraries, headers, pkg-config files, providers and
  the openssl3 command, plus an ld.so.conf entry and CA-store links; it
  does not ship the Perl CA management scripts.
