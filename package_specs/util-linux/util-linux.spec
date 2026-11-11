Name:       util-linux
Version:    2.42.4
Release:    3
Summary:    util-linux is a random collection of Linux utilities
License:    GPL-2.0-or-later AND GPL-1.0-or-later AND GPL-2.0-only AND GPL-3.0-or-later AND LGPL-2.1-or-later AND MIT AND BSD-2-Clause AND BSD-3-Clause AND BSD-4-Clause-UC AND EUPL-1.2 AND ISC AND 0BSD
URL:        https://github.com/util-linux/util-linux
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
util-linux is a random collection of Linux utilities

%package lang
Summary:    util-linux translations
Requires:   util-linux = %{version}-%{release}

%description lang
Translations for util-linux.

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
# systemd's getty units and the system-user shell expect /usr/sbin paths.
mkdir -p %{buildroot}/usr/sbin
ln -sf ../bin/agetty %{buildroot}/usr/sbin/agetty
ln -sf ../bin/nologin %{buildroot}/usr/sbin/nologin
chmod 4755 %{buildroot}%{_bindir}/mount %{buildroot}%{_bindir}/umount
chmod 2755 %{buildroot}%{_bindir}/wall
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/util-linux.filelist
%files lang -f %{_sourcedir}/util-linux-lang.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.42.4-3
- Record the verified license (GPL-2.0-or-later AND GPL-1.0-or-later AND GPL-2.0-only AND GPL-3.0-or-later AND LGPL-2.1-or-later AND MIT AND BSD-2-Clause AND BSD-3-Clause AND BSD-4-Clause-UC AND EUPL-1.2 AND ISC AND 0BSD): README.licensing (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.42.4-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 2.42.4-1
- Update to 2.42.4 (current upstream version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.42.2-2
- Split lang, devel payload into util-linux-lang, util-linux-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.42.2
- Replace directory globs with a generated static filelist
* Fri Oct 30 2026 browneye <build@browneye.invalid> 2.42.2
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 4.0.3-1
- Version bump

* Sun Jun 18 2023 Chris Statzer <chris.statzer@gmail.com> 2.33.1-2
- /sbin/raw is no longer built automatically with kernerls past 5.4 as raw.h was removed from kernel headers
