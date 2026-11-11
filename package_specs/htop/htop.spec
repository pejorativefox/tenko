Name:       htop
Version:    3.5.3
Release:    1
Summary:    Interactive process viewer
License:    GPL-2.0-or-later
URL:        https://htop.dev
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
htop is an interactive system-monitor process viewer for Linux.  It shows a
frequently updated list of the running processes, sorted by CPU, memory or
other columns, and lets you search, filter, renice, kill, trace and inspect
them from a full-screen ncurses interface.  It also displays per-core CPU,
memory and swap meters, a tree view of the process hierarchy and per-process
open files and environment.

htop is not part of the base set; the user approved upstream 3.5.3 as
the version-policy exception.

%prep
%setup -q

%build
# The base system ships ncurses but no libcap, libnl, lm_sensors or hwloc
# development files.  Disable those optional features explicitly so the
# result does not depend on which headers happen to be present at build time.
%configure            \
    --disable-capabilities \
    --disable-delayacct    \
    --disable-sensors      \
    --disable-hwloc
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/htop.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.5.3-1
- Update to upstream 3.5.3.  htop is not in the base set; the user
  approved this upstream release as the version-policy exception.
- Source: https://github.com/htop-dev/htop/releases/download/3.5.3/htop-3.5.3.tar.xz
  md5 587f0d8ca67592ca199abef235dadb68
  sha256 a8b164386494cb85bb255a415a3f5f80afe7a0c4491da5d113b3a0f951087e65
- Changes from 3.2.2: GPU meter, per-process file-descriptor and delay
  accounting meters, new screens (backtrace) and dynamic columns, a
  rewritten settings file with migration, Unicode/wide-character fixes,
  and many crash and portability fixes.
- Build with the base ncurses only: capabilities, delay accounting,
  sensors and hwloc remain disabled because their development files are
  not part of the base system.
- The installed file set is unchanged (binary, desktop entry, man page,
  pixmap and scalable icon).
