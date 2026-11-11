Name:       bwm-ng
Version:    0.6.3
Release:    1
Summary:    Console-based live network and disk bandwidth monitor
License:    GPL-2.0-or-later
URL:        https://github.com/vgropp/bwm-ng
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
bwm-ng (Bandwidth Monitor NG) is a small, simple, console-based live
network and disk bandwidth monitor.  It reads the kernel counters through
/proc/net/dev, getifaddrs, /proc/diskstats or libstatgrab, and can show
per-interface rates, totals, averages and maximums in a curses interface
or as a single-shot or continuous plain-text report suitable for scripts.

bwm-ng is not part of the base set; the user approved upstream 0.6.3
as the version-policy exception.

%prep
%setup -q

%build
# The tarball is a git archive with no generated configure script.
./autogen.sh --prefix=/usr --with-ncurses
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/bwm-ng.filelist

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.6.3-1
- Update to upstream 0.6.3 (was a 0.6.2 stub that was never built).
  bwm-ng is not in the base set; the user approved this upstream
  release as the version-policy exception.
- Source: https://github.com/vgropp/bwm-ng/archive/v0.6.3.tar.gz
  md5 eb343c2b806c5e9a40611fc39e907a3d
  sha256 c1a552b6ff48ea3e4e10110a7c188861abc4750befc67c6caaba8eb3ecf67f46
- Changes from 0.6.2: getifaddrs backend fixes, a rewritten /proc/diskstats
  parser (partitions and whole disks), correct counter wrap-around
  handling, and build-system updates for modern autotools.
- Build with ncurses (the base system's wide-character ncurses) instead of
  plain curses; the tarball ships no configure, so autogen.sh is run.
- The package installs the binary and its man page.
