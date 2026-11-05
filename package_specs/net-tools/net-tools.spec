Name:       net-tools
Version:    2.10
Release:    2
Summary:    Various networking tools
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The Net-tools package is a collection of programs for controlling the network subsystem of the Linux kernel.

%prep
%setup -q

%build
export BINDIR=/usr/bin SBINDIR=/usr/bin
yes "" | make config
sed -e /ROM/s/1/0/  \
    -e /X25/s/1/0/  \
    -e /ROSE/s/1/0/ \
    -i config.h
%make_build

%install
rm -rf %{buildroot}
export BINDIR=/usr/bin SBINDIR=/usr/bin
make DESTDIR=%{buildroot} install
rm -f %{buildroot}/usr/bin/{nis,yp}domainname
rm -f %{buildroot}/usr/bin/{hostname,dnsdomainname,domainname,ifconfig}
rm -rf %{buildroot}/usr/share/man

%files
/usr/bin/arp
/usr/bin/ipmaddr
/usr/bin/iptunnel
/usr/bin/mii-tool
/usr/bin/nameif
/usr/bin/netstat
/usr/bin/plipconfig
/usr/bin/rarp
/usr/bin/route
/usr/bin/slattach

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.10-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING, plus lib/*.c "either version 2 ... or any later version" (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.10-1
- Sync with BLFS r13.1

* Wed Aug 19 2020 Chris Statzer <chris.statzer@qq.com> 1.60
- Initial RPM

