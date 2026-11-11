Name:       ntp
Version:    4.2.8p18
Release:    3
Summary:    NTP time sync daemon
License:    NTP
Source0:    %{name}-%{version}.tar.gz
Source1:    ntp.conf
Source2:    ntpd.conf
Source3:    ntpd.service
Patch0:     %{name}-%{version}-openssl_4-1.patch
Prefix:     /usr

%description
NTP Time sync daemon

%prep
%setup
sed -i 's/getclock/getclock memchr/'               sntp/m4/ntp_libntp.m4
sed -i 's/pthread_detach(NULL)/pthread_detach(0)/' sntp/m4/openldap-thread-check.m4
autoreconf -fiv
sed -i "/ep.*FAILED/,+4s/ep/ep2/" ntpd/ntp_io.c
%patch -P 0 -p1

%build
# libmd ships a stricter md5.h than the bundled isc one; gcc 16 promotes
# the resulting pointer-type mismatch to an error.
export CFLAGS="$CFLAGS -Wno-error=incompatible-pointer-types"
%configure --bindir=/usr/sbin   \
           --sysconfdir=/etc    \
           --enable-linuxcaps   \
           --with-lineeditlibs=readline \
           --docdir=/usr/share/doc/ntp-%{version}
%make_build

%install
rm -rf %{buildroot}
%make_install
# update-leap is not packaged: its cargo-culted CPAN dependencies are not
# available (see the changelog).
rm -f %{buildroot}/usr/sbin/update-leap \
      %{buildroot}/usr/share/man/man1/update-leap.1*

mkdir -pv %{buildroot}/etc/finit.d/available
cp %{SOURCE1} %{buildroot}/etc
cp %{SOURCE2} %{buildroot}/etc/finit.d/available

mkdir -pv %{buildroot}/etc/service.d
cp %{SOURCE3} %{buildroot}/etc/service.d

%post
groupadd -g 87 ntp &&
useradd -c "Network Time Protocol" -d /var/lib/ntp -u 87 \
        -g ntp -s /bin/false ntp
install -v -o ntp -g ntp -d /var/lib/ntp

%files -f %{_sourcedir}/ntp.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.2.8p18-3
- Replace NO_IDEA with the verified license (NTP): COPYRIGHT (NTP copyright notice) (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 4.2.8p18-2
- Drop the ntp-leap subpackage (update-leap).  It needs the CPAN modules
  IO::Socket::SSL and Net::SSLeay, which are not in the base set, so the
  subpackage was never installable; the user chose not to package it.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 4.2.8p18-1
- Sync with the base set

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 4.2.8p14-2
- Added default configuration and finit service

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 4.2.8p14-1
- Initial RPM

