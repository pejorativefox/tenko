Name:       socat
Version:    1.8.1.3
Release:    1
Summary:    Multipurpose relay for bidirectional data transfer
License:    GPL-2.0-only WITH openvpn-openssl-exception
URL:        http://www.dest-unreach.org/socat/
Source0:    %{name}-%{version}.tar.gz
# OpenSSL 4 makes ASN1_STRING opaque; use the accessors (OpenSSL >= 1.1).
Patch0:     %{name}-%{version}-openssl4.patch
Prefix:     /usr

BuildRequires: openssl
BuildRequires: readline
BuildRequires: ncurses

%description
socat relays data between two bidirectional byte streams: files, pipes,
devices, TCP/UDP/SCTP sockets (IPv4 and IPv6), UNIX sockets, TLS
connections, PTYs and processes.  It is useful for debugging network
services and for talking to UNIX sockets such as a QEMU monitor or serial
console.  The package also ships filan and procan.

%prep
%setup -q
%patch -P 0 -p1

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/socat.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 1.8.1.3-1
- New package, not in the base set: latest upstream stable release
  (1.8.1.3, checked 2026-11-11).  Useful for QEMU monitor and serial
  sockets on build hosts (tenko-osdev).
- Patch xio-openssl.c to read the subjectAltName IP address through
  ASN1_STRING_get0_data()/ASN1_STRING_length(); OpenSSL 4 made
  ASN1_STRING opaque.
