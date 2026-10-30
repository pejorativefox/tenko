Name:       util-linux
Version:    2.42.2
Release:    1
Summary:    util-linux is a random collection of Linux utilities
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
util-linux is a random collection of Linux utilities

%prep
%setup -q

%build
%configure   ADJTIME_PATH=/var/lib/hwclock/adjtime \
            --disable-chfn-chsh  \
            --disable-login      \
            --disable-nologin    \
            --disable-su         \
            --disable-setpriv    \
            --disable-runuser    \
            --disable-pylibmount \
            --disable-static     \
            --disable-liblastlog2 \
            --runstatedir=/run    \
            --without-python     \
            --without-systemd    \
            --without-systemdsystemunitdir \
            --docdir=/usr/share/doc/util-linux-%{version}
%make_build

%install
rm -rf %{buildroot}
# install hooks chown/chgrp to root/tty, which a non-root build cannot do
make -k install DESTDIR=%{buildroot} || true
chmod 4755 %{buildroot}%{_bindir}/mount %{buildroot}%{_bindir}/umount
chmod 2755 %{buildroot}%{_bindir}/wall
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/
/usr/include/
/usr/lib64/
/usr/sbin/
/usr/share/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.42.2
- Sync with LFS r13.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 4.0.3-1
- Version bump

* Sun Jun 18 2023 Chris Statzer <chris.statzer@gmail.com> 2.33.1-2
- /sbin/raw is no longer built automatically with kernerls past 5.4 as raw.h was removed from kernel headers
