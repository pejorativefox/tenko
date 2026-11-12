Name:       tzdb
Version:    2026f
Release:    4
Summary:    The Time Zone Database
License:    Public Domain
URL:        https://www.iana.org/time-zones
Source0:    tzcode%{version}.tar.gz
Source1:    tzdata%{version}.tar.gz
Prefix:     /usr

%description
The Time Zone Database (often called tz or zoneinfo) contains code and
data that represent the history of local time for many representative
locations around the globe.

%prep
%setup -q -c -T -a 0 -a 1 -n %{name}-%{version}

%build
%make_build CC=%{__cc}

%install
rm -rf %{buildroot}
%make_install CC=%{__cc} LIBDIR=%{_libdir}

# glibc already ships the timezone tools; shipping them here makes the
# package uninstallable next to a base system.
rm -f %{buildroot}%{_bindir}/tzselect \
      %{buildroot}%{_bindir}/zdump \
      %{buildroot}/usr/sbin/zic

# man-pages owns /usr/share/man and already ships tzfile(5), zic(8),
# zdump(8) and tzselect(8).  Duplicating them here made zic.8.gz a file
# conflict, so man-pages and tzdb could not be installed together.  Keep the
# newctime/newtzset pages, which man-pages does not provide.
rm -f %{buildroot}%{_mandir}/man5/tzfile.5* \
      %{buildroot}%{_mandir}/man8/tzselect.8* \
      %{buildroot}%{_mandir}/man8/zdump.8* \
      %{buildroot}%{_mandir}/man8/zic.8*

%files -f %{_sourcedir}/tzdb.filelist

%changelog
* Thu Nov 12 2026 tenko <build@tenko.invalid> 2026f-4
- Install libtz.a in /usr/lib64.  The upstream Makefile defaults LIBDIR
  to $(TOPDIR)/usr/lib, so the static archive landed in /usr/lib.

* Mon Nov 09 2026 browneye <build@browneye.invalid> 2026f-3
- Drop the tzfile(5), zic(8), zdump(8) and tzselect(8) manual pages:
  man-pages owns /usr/share/man and already provides them.  tzdb's zic.8.gz
  differed from man-pages' copy and produced a file conflict, so tzdb and
  man-pages could not be installed in the same transaction.  The
  newctime(3)/newtzset(3) pages, zoneinfo data, libtz.a and /etc/localtime
  are unchanged.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2026f-2
- Do not package tzselect, zdump or zic: glibc 2.44 already owns those
  paths, so tzdb 2026f-1 could not be installed next to the base system.
  The package now provides the zoneinfo data, libtz.a, man pages and
  /etc/localtime only.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2026f-1
- Not shipped as a package in the base set; 2026f matches the documented
  tzdata entity and is the current upstream release (2026-11-05).
- Upstream no longer publishes tzdb-*.tar.gz; build the official
  tzcode2026f and tzdata2026f tarballs in one tree.
- Run the upstream make (no lzip) and package zic, zdump, tzselect,
  libtz.a, the man pages and the zoneinfo tree, including the
  /etc/localtime symlink that upstream's install target creates.
- Refresh %files from the actual install.

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 2020a
- Initial RPM
