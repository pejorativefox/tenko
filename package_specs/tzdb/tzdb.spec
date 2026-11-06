Name:       tzdb
Version:    2026f
Release:    2
Summary:    The Time Zone Database
License:    Public Domain
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
%make_install CC=%{__cc}

# glibc already ships the timezone tools; shipping them here makes the
# package uninstallable next to a base system.
rm -f %{buildroot}%{_bindir}/tzselect \
      %{buildroot}%{_bindir}/zdump \
      %{buildroot}/usr/sbin/zic

%files -f %{_sourcedir}/tzdb.filelist

%changelog
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
