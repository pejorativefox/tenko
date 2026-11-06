Name:       proxychains-ng
Version:    4.17
Release:    1
Summary:    Preloader that redirects TCP connections through proxies
License:    GPL-2.0-or-later
URL:        https://github.com/rofl0r/proxychains-ng
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
ProxyChains-NG is a preloader which hooks calls to sockets in dynamically
linked programs and redirects them through one or more SOCKS4a, SOCKS5 or HTTP
proxies.  It supports TCP only (no UDP or ICMP).

ProxyChains-NG is not part of the base set; the user approved upstream
4.17 as the version-policy exception.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
make install-config DESTDIR=%{buildroot}

%files
%config(noreplace) /etc/proxychains.conf
/usr/bin/proxychains4
/usr/bin/proxychains4-daemon
/usr/lib64/libproxychains4.so
%doc README COPYING AUTHORS

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.17-1
- Update to upstream 4.17.  proxychains-ng is not in the base set;
  the user approved this upstream release as the version-policy exception.
- Source: https://github.com/rofl0r/proxychains-ng/releases/download/v4.17/proxychains-ng-4.17.tar.xz
  md5 16ac3c14ca90d74ea64fa6ec81e70548
  sha256 36ddc7f64cb3df2ca4170627c6e0f0dea33d1a6d0730629dff6f5c633f2006f9
- Changes from 4.16: close_range hook for newer OpenSSH, DNS error handling
  fixes, multithread double-close fix and configure-script improvements.
- Build with the upstream configure script at prefix=/usr, libdir=/usr/lib64
  and sysconfdir=/etc; install the default configuration as
  /etc/proxychains.conf, matching the compiled-in SYSCONFDIR.
- Ship README, COPYING and AUTHORS under the package documentation.
