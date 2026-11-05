Name:       openssl
Version:    4.1.0
Release:    4
Summary:    OpenSSL software library
License:    Apache-2.0
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

# CA.pl loads WWW::Curl only for the optional -curl path.
%global __requires_exclude ^perl\\(WWW::Curl::Easy\\)$

AutoReq: no

Requires:   openssl-libs = %{version}-%{release}

%description
OpenSSL is a software library for applications that provide secure communications over computer networks 

%package libs
Summary:    OpenSSL runtime libraries and configuration
License:    Apache-2.0
Requires:   libc.so.6()(64bit)

%description libs
The OpenSSL runtime libraries (libssl and libcrypto), the legacy provider
module and the default OpenSSL configuration under /etc/ssl.  Runtime-only
installs need this package; it does not require the openssl command-line
tool or Perl.

%package perl
Summary:    OpenSSL Perl helper scripts
License:    Apache-2.0
Requires:   openssl = %{version}-%{release}
Requires:   perl

%description perl
The Perl helper script shipped with OpenSSL (CA.pl).  The tsget
client is not packaged because it requires Net::Curl::Easy, which is
not available.
Install this package only when the openssl command-line tool is needed;
the library and CLI packages no longer depend on Perl.

%prep
%setup

%build
./config --prefix=/usr         \
         --openssldir=/etc/ssl \
         shared                \
         zlib-dynamic
%make_build

%install
rm -rf %{buildroot}
sed -i '/INSTALL_LIBS/s/libcrypto.a libssl.a//' Makefile
%make_install MANSUFFIX=ssl
rm -vf %{buildroot}%{_infodir}/dir*
rm -rf %{buildroot}/usr/share/doc/openssl
rm -rf %{buildroot}/usr/share/man
# tsget/tsget.pl need Net::Curl::Easy, which the distro does not provide.
rm -f %{buildroot}/etc/ssl/misc/tsget %{buildroot}/etc/ssl/misc/tsget.pl

%files -f %{_sourcedir}/openssl.filelist
%files libs -f %{_sourcedir}/openssl-libs.filelist
%files perl -f %{_sourcedir}/openssl-perl.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.1.0-4
- Stop shipping tsget/tsget.pl: OpenSSL 4.1's client requires
  Net::Curl::Easy, which is not packaged (and not in LFS/BLFS).  The
  auto-generated perl(Net::Curl::Easy) require made openssl-perl
  uninstallable.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.1.0-3
- Record the verified license (Apache-2.0): LICENSE.txt (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.1.0-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 4.1.0-1
- Update to 4.1.0 (current LFS/BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.0.2-2
- Split runtime libraries, devel files and Perl helpers out of the main
  package so openssl/openssl-libs no longer require Perl (size audit §7)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.0.1
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 3.1.2-1
- Version bump
