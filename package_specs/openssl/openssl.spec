Name:       openssl
Version:    4.0.2
Release:    2
Summary:    OpenSSL software library
License:    GPL3
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
License:    GPL3
Requires:   libc.so.6()(64bit)

%description libs
The OpenSSL runtime libraries (libssl and libcrypto), the legacy provider
module and the default OpenSSL configuration under /etc/ssl.  Runtime-only
installs need this package; it does not require the openssl command-line
tool or Perl.

%package devel
Summary:    OpenSSL development headers and libraries
License:    GPL3
Requires:   openssl-libs = %{version}-%{release}

%description devel
Headers, pkg-config metadata, CMake config files and the unversioned linker
symlinks needed to build software against OpenSSL.

%package perl
Summary:    OpenSSL Perl helper scripts
License:    GPL3
Requires:   openssl = %{version}-%{release}
Requires:   perl

%description perl
The Perl helper scripts shipped with OpenSSL (CA.pl, tsget/tsget.pl).
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

%files -f %{_sourcedir}/openssl.filelist
%files libs -f %{_sourcedir}/openssl-libs.filelist
%files devel -f %{_sourcedir}/openssl-devel.filelist
%files perl -f %{_sourcedir}/openssl-perl.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.0.2-2
- Split runtime libraries, devel files and Perl helpers out of the main
  package so openssl/openssl-libs no longer require Perl (size audit §7)

* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.0.1
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 3.1.2-1
- Version bump
