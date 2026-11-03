Name:       ntp
Version:    4.2.8p18
Release:    2
Summary:    NTP time sync daemon
License:    NO_IDEA
Source0:    %{name}-%{version}.tar.gz
Source1:    ntp.conf
Source2:    ntpd.conf
Source3:    ntpd.service
Source4:    %{name}-%{version}-openssl_4-1.patch
Prefix:     /usr

%description
NTP Time sync daemon

%prep
%setup
sed -i 's/getclock/getclock memchr/'               sntp/m4/ntp_libntp.m4
sed -i 's/pthread_detach(NULL)/pthread_detach(0)/' sntp/m4/openldap-thread-check.m4
autoreconf -fiv
sed -i "/ep.*FAILED/,+4s/ep/ep2/" ntpd/ntp_io.c
patch -Np1 -i %{SOURCE4}

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
# in LFS/BLFS (see the changelog).
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

%files
/etc/finit.d/available/ntpd.conf
/etc/ntp.conf
/etc/service.d/ntpd.service
/usr/sbin/calc_tickadj
/usr/sbin/ntp-keygen
/usr/sbin/ntp-wait
/usr/sbin/ntpd
/usr/sbin/ntpdate
/usr/sbin/ntpdc
/usr/sbin/ntpq
/usr/sbin/ntptime
/usr/sbin/ntptrace
/usr/sbin/sntp
/usr/sbin/tickadj
/usr/share/doc/ntp-4.2.8p18/html/.datecheck
/usr/share/doc/ntp-4.2.8p18/html/access.html
/usr/share/doc/ntp-4.2.8p18/html/accopt.html
/usr/share/doc/ntp-4.2.8p18/html/assoc.html
/usr/share/doc/ntp-4.2.8p18/html/audio.html
/usr/share/doc/ntp-4.2.8p18/html/authentic.html
/usr/share/doc/ntp-4.2.8p18/html/authopt.html
/usr/share/doc/ntp-4.2.8p18/html/autokey.html
/usr/share/doc/ntp-4.2.8p18/html/bugs.html
/usr/share/doc/ntp-4.2.8p18/html/build.html
/usr/share/doc/ntp-4.2.8p18/html/clock.html
/usr/share/doc/ntp-4.2.8p18/html/clockopt.html
/usr/share/doc/ntp-4.2.8p18/html/cluster.html
/usr/share/doc/ntp-4.2.8p18/html/comdex.html
/usr/share/doc/ntp-4.2.8p18/html/config.html
/usr/share/doc/ntp-4.2.8p18/html/confopt.html
/usr/share/doc/ntp-4.2.8p18/html/copyright.html
/usr/share/doc/ntp-4.2.8p18/html/debug.html
/usr/share/doc/ntp-4.2.8p18/html/decode.html
/usr/share/doc/ntp-4.2.8p18/html/discipline.html
/usr/share/doc/ntp-4.2.8p18/html/discover.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver1.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver10.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver11.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver12.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver16.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver18.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver19.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver20.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver22.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver26.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver27.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver28.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver29.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver3.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver30.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver31.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver32.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver33.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver34.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver35.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver36.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver37.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver38.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver39.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver4.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver40-ja.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver40.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver42.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver43.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver44.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver45.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver46.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver5.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver6.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver7.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver8.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/driver9.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/icons/home.gif
/usr/share/doc/ntp-4.2.8p18/html/drivers/icons/mail2.gif
/usr/share/doc/ntp-4.2.8p18/html/drivers/mx4200data.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/oncore-shmem.html
/usr/share/doc/ntp-4.2.8p18/html/drivers/scripts/footer.txt
/usr/share/doc/ntp-4.2.8p18/html/drivers/scripts/style.css
/usr/share/doc/ntp-4.2.8p18/html/drivers/tf582_4.html
/usr/share/doc/ntp-4.2.8p18/html/extern.html
/usr/share/doc/ntp-4.2.8p18/html/filter.html
/usr/share/doc/ntp-4.2.8p18/html/hints.html
/usr/share/doc/ntp-4.2.8p18/html/hints/a-ux
/usr/share/doc/ntp-4.2.8p18/html/hints/aix
/usr/share/doc/ntp-4.2.8p18/html/hints/bsdi
/usr/share/doc/ntp-4.2.8p18/html/hints/changes
/usr/share/doc/ntp-4.2.8p18/html/hints/decosf1
/usr/share/doc/ntp-4.2.8p18/html/hints/decosf2
/usr/share/doc/ntp-4.2.8p18/html/hints/freebsd
/usr/share/doc/ntp-4.2.8p18/html/hints/hpux
/usr/share/doc/ntp-4.2.8p18/html/hints/linux
/usr/share/doc/ntp-4.2.8p18/html/hints/mpeix
/usr/share/doc/ntp-4.2.8p18/html/hints/notes-xntp-v3
/usr/share/doc/ntp-4.2.8p18/html/hints/parse
/usr/share/doc/ntp-4.2.8p18/html/hints/refclocks
/usr/share/doc/ntp-4.2.8p18/html/hints/rs6000
/usr/share/doc/ntp-4.2.8p18/html/hints/sco.html
/usr/share/doc/ntp-4.2.8p18/html/hints/sgi
/usr/share/doc/ntp-4.2.8p18/html/hints/solaris-dosynctodr.html
/usr/share/doc/ntp-4.2.8p18/html/hints/solaris.html
/usr/share/doc/ntp-4.2.8p18/html/hints/solaris.xtra.4023118
/usr/share/doc/ntp-4.2.8p18/html/hints/solaris.xtra.4095849
/usr/share/doc/ntp-4.2.8p18/html/hints/solaris.xtra.S99ntpd
/usr/share/doc/ntp-4.2.8p18/html/hints/solaris.xtra.patchfreq
/usr/share/doc/ntp-4.2.8p18/html/hints/sun4
/usr/share/doc/ntp-4.2.8p18/html/hints/svr4-dell
/usr/share/doc/ntp-4.2.8p18/html/hints/svr4_package
/usr/share/doc/ntp-4.2.8p18/html/hints/todo
/usr/share/doc/ntp-4.2.8p18/html/hints/vxworks.html
/usr/share/doc/ntp-4.2.8p18/html/hints/winnt.html
/usr/share/doc/ntp-4.2.8p18/html/history.html
/usr/share/doc/ntp-4.2.8p18/html/howto.html
/usr/share/doc/ntp-4.2.8p18/html/huffpuff.html
/usr/share/doc/ntp-4.2.8p18/html/icons/home.gif
/usr/share/doc/ntp-4.2.8p18/html/icons/mail2.gif
/usr/share/doc/ntp-4.2.8p18/html/icons/sitemap.png
/usr/share/doc/ntp-4.2.8p18/html/index.html
/usr/share/doc/ntp-4.2.8p18/html/kern.html
/usr/share/doc/ntp-4.2.8p18/html/kernpps.html
/usr/share/doc/ntp-4.2.8p18/html/keygen.html
/usr/share/doc/ntp-4.2.8p18/html/leap.html
/usr/share/doc/ntp-4.2.8p18/html/miscopt.html
/usr/share/doc/ntp-4.2.8p18/html/monopt.html
/usr/share/doc/ntp-4.2.8p18/html/msyslog.html
/usr/share/doc/ntp-4.2.8p18/html/ntp-wait.html
/usr/share/doc/ntp-4.2.8p18/html/ntp_conf.html
/usr/share/doc/ntp-4.2.8p18/html/ntpd.html
/usr/share/doc/ntp-4.2.8p18/html/ntpdate.html
/usr/share/doc/ntp-4.2.8p18/html/ntpdc.html
/usr/share/doc/ntp-4.2.8p18/html/ntpdsim.html
/usr/share/doc/ntp-4.2.8p18/html/ntpdsim_new.html
/usr/share/doc/ntp-4.2.8p18/html/ntpq.html
/usr/share/doc/ntp-4.2.8p18/html/ntptime.html
/usr/share/doc/ntp-4.2.8p18/html/ntptrace.html
/usr/share/doc/ntp-4.2.8p18/html/orphan.html
/usr/share/doc/ntp-4.2.8p18/html/parsedata.html
/usr/share/doc/ntp-4.2.8p18/html/parsenew.html
/usr/share/doc/ntp-4.2.8p18/html/pic/9400n.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/alice11.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/alice13.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/alice15.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/alice23.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/alice31.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/alice32.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/alice35.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/alice38.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/alice44.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/alice47.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/alice51.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/alice61.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/barnstable.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/beaver.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/boom3.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/boom3a.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/boom4.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/broad.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/bustardfly.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/c51.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/description.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/discipline.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/dogsnake.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/driver29.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/driver43_1.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/driver43_2.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/fg6021.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/fg6039.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/fig_3_1.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/flatheads.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/flt1.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/flt2.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/flt3.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/flt4.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/flt5.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/flt6.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/flt7.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/flt8.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/flt9.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/freq1211.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/gadget.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/gps167.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/group.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/hornraba.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/igclock.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/neoclock4x.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/offset1211.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/oncore_evalbig.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/oncore_remoteant.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/oncore_utplusbig.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/oz2.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/panda.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/pd_om006.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/pd_om011.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/peer.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/pogo.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/pogo1a.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/pogo3a.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/pogo4.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/pogo5.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/pogo6.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/pogo7.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/pogo8.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/pzf509.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/pzf511.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/rabbit.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/radio2.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/sheepb.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/stack1a.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/stats.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/sx5.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/thunderbolt.jpg
/usr/share/doc/ntp-4.2.8p18/html/pic/time1.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/tonea.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/tribeb.gif
/usr/share/doc/ntp-4.2.8p18/html/pic/wingdorothy.gif
/usr/share/doc/ntp-4.2.8p18/html/poll.html
/usr/share/doc/ntp-4.2.8p18/html/pps.html
/usr/share/doc/ntp-4.2.8p18/html/prefer.html
/usr/share/doc/ntp-4.2.8p18/html/quick.html
/usr/share/doc/ntp-4.2.8p18/html/rate.html
/usr/share/doc/ntp-4.2.8p18/html/rdebug.html
/usr/share/doc/ntp-4.2.8p18/html/refclock.html
/usr/share/doc/ntp-4.2.8p18/html/release.html
/usr/share/doc/ntp-4.2.8p18/html/scripts/accopt.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/audio.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/authopt.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/clockopt.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/command.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/config.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/confopt.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/external.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/footer.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/hand.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/install.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/manual.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/misc.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/miscopt.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/monopt.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/refclock.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/special.txt
/usr/share/doc/ntp-4.2.8p18/html/scripts/style.css
/usr/share/doc/ntp-4.2.8p18/html/select.html
/usr/share/doc/ntp-4.2.8p18/html/sitemap.html
/usr/share/doc/ntp-4.2.8p18/html/sntp.html
/usr/share/doc/ntp-4.2.8p18/html/stats.html
/usr/share/doc/ntp-4.2.8p18/html/tickadj.html
/usr/share/doc/ntp-4.2.8p18/html/warp.html
/usr/share/doc/ntp-4.2.8p18/html/xleave.html
/usr/share/doc/ntp-4.2.8p18/ntp-keygen.html
/usr/share/doc/ntp-4.2.8p18/ntp-wait.html
/usr/share/doc/ntp-4.2.8p18/ntp.conf.html
/usr/share/doc/ntp-4.2.8p18/ntp.keys.html
/usr/share/doc/ntp-4.2.8p18/ntpd.html
/usr/share/doc/ntp-4.2.8p18/ntpdc.html
/usr/share/doc/ntp-4.2.8p18/ntpq.html
/usr/share/doc/ntp-4.2.8p18/ntpsnmpd.html
/usr/share/doc/ntp-4.2.8p18/ntpsweep.html
/usr/share/doc/ntp-4.2.8p18/ntptrace.html
/usr/share/doc/ntp-4.2.8p18/sntp.html
/usr/share/doc/ntp-4.2.8p18/update-leap.html
/usr/share/man/man1/calc_tickadj.1.gz
/usr/share/man/man1/ntp-keygen.1.gz
/usr/share/man/man1/ntp-wait.1.gz
/usr/share/man/man1/ntpd.1.gz
/usr/share/man/man1/ntpdc.1.gz
/usr/share/man/man1/ntpq.1.gz
/usr/share/man/man1/ntptrace.1.gz
/usr/share/man/man1/sntp.1.gz
/usr/share/man/man5/ntp.conf.5.gz
/usr/share/man/man5/ntp.keys.5.gz
/usr/share/ntp/lib/NTP/Util.pm

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 4.2.8p18-2
- Drop the ntp-leap subpackage (update-leap).  It needs the CPAN modules
  IO::Socket::SSL and Net::SSLeay, which are not in LFS/BLFS, so the
  subpackage was never installable; the user chose not to package it.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 4.2.8p18-1
- Sync with BLFS r13.1

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 4.2.8p14-2
- Added default configuration and finit service

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 4.2.8p14-1
- Initial RPM

