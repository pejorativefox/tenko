Name:       procps-ng
Version:    4.0.7
Release:    1
Summary:    Process monitoring utilities
License:    GPL3
Source0:    procps-ng-%{version}.tar.xz
Prefix:     /usr

%description
The Procps-ng package contains programs for monitoring processes. 

%prep
%setup -q 

%build
%configure  --docdir=/usr/share/doc/procps-ng-%{version} \
            --disable-static                         \
            --disable-kill

%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/bin/free
/usr/bin/pgrep
/usr/bin/pidof
/usr/bin/pkill
/usr/bin/pmap
/usr/bin/ps
/usr/bin/pwdx
/usr/bin/slabtop
/usr/bin/tload
/usr/bin/top
/usr/bin/uptime
/usr/bin/vmstat
/usr/bin/w
/usr/bin/watch
/usr/bin/pidwait
/usr/include/libproc2/diskstats.h
/usr/include/libproc2/meminfo.h
/usr/include/libproc2/misc.h
/usr/include/libproc2/pids.h
/usr/include/libproc2/slabinfo.h
/usr/include/libproc2/stat.h
/usr/include/libproc2/vmstat.h
/usr/include/libproc2/xtra-procps-debug.h
/usr/lib64/libproc2.so
/usr/lib64/libproc2.so.1
/usr/lib64/libproc2.so.1.0.2
/usr/lib64/pkgconfig/libproc2.pc
/usr/bin/hugetop
/usr/bin/sysctl
/usr/share/doc/
/usr/share/locale/
/usr/share/man/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.0.7
- Sync with LFS r13.1

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 4.0.3-1
- Version bump
