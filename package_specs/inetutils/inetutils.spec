Name:       inetutils
Version:    2.8
Release:    1
Summary:    Collection of common network programs.
License:    GPL3
Source0:    inetutils-2.8.tar.gz
Prefix:     /usr

%description
Collection of common network programs.

%prep
%setup -q

%build
CFLAGS="$CFLAGS -Wformat"
%configure  --disable-logger     \
            --disable-whois      \
            --disable-rcp        \
            --disable-rexec      \
            --disable-rlogin     \
            --disable-rsh        \
            --disable-servers 
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/talk
/usr/bin/dnsdomainname
/usr/bin/ftp
/usr/bin/hostname
/usr/bin/ifconfig
/usr/bin/ping
/usr/bin/ping6
/usr/bin/telnet
/usr/bin/tftp
/usr/bin/traceroute
/usr/share/info/inetutils.info.gz
/usr/share/man/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.8
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 2.4-1
- Version bump

* Mon Jun 19 2023 Chris Statzer <chris.statzer@gmail.com> 1.9.4-1
- Removed the talk binary as it's no longer being built.
