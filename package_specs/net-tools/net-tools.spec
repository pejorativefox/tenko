Name:       net-tools
Version:    2.10
Release:    1
Summary:    Various networking tools
License:    GPL
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
make DESTDIR=%{buildroot} install
rm -f %{buildroot}/usr/bin/{nis,yp}domainname
rm -f %{buildroot}/usr/bin/{hostname,dnsdomainname,domainname,ifconfig}
rm -rf %{buildroot}/usr/share/man

%files
/bin/dnsdomainname
/bin/domainname
/bin/hostname
/bin/ifconfig
/bin/netstat
/bin/nisdomainname
/bin/route
/bin/ypdomainname
/sbin/arp
/sbin/ipmaddr
/sbin/iptunnel
/sbin/mii-tool
/sbin/nameif
/sbin/plipconfig
/sbin/rarp
/sbin/slattach

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.10-1
- Sync with BLFS r13.1

* Wed Aug 19 2020 Chris Statzer <chris.statzer@qq.com> 1.60
- Initial RPM

