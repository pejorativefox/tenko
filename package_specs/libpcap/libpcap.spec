Name:       libpcap
Version:    1.10.7
Release:    3
Summary:    Packet capture library
License:    BSD-3-Clause
URL:        https://www.tcpdump.org/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: dbus-libs
BuildRequires: libnl
BuildRequires: dbus-daemon

%description
libpcap provides functions for user-level packet capture, used in low-level
network monitoring.  Nmap links against it for its packet-capture engine.

%prep
%setup -q

%build
%configure --prefix=/usr
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -rf %{buildroot}%{_docdir}/%{name}-%{version}/html

%files -f %{_sourcedir}/libpcap.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.10.7-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.10.7-1
- New package (libpcap 1.10.7, the version Nmap 7.991 uses).
- Source: https://www.tcpdump.org/release/libpcap-1.10.7.tar.gz
  md5 95cf0ff1fb0328e309d5e0d8d589c558
  sha256 0b394ac90dbc0a9838ff97468e05c9c9a3e873dec2514cd58db65d859d296e31
- Build with ./configure --prefix=/usr && make && make install.
  The HTML API docs are not shipped.
