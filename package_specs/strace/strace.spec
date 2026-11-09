Name:       strace
Version:    7.3
Release:    1
Summary:    System call and signal tracer
License:    LGPL-2.1-or-later
URL:        https://strace.io/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
strace is a diagnostic, debugging and instructional userspace tracer.  It
records the system calls and signals received by a process, together with
their arguments and return values, and can filter, count, time and summarise
them.  It is commonly used to debug programs and to inspect how they interact
with the kernel.  The package also ships strace-log-merge, which combines the
per-process trace files produced by strace -ff into one chronological log.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/strace.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 7.3-1
- Initial package at the latest stable upstream release, strace 7.3
  (published 2026-10-22), from the upstream release tarball.
- Licence verified as LGPL-2.1-or-later from COPYING ("GNU Lesser General
  Public License ... version 2.1 ... or (at your option) any later
  version"); the test suite's separate GPL-2.0-or-later terms do not apply
  to the installed binaries.
- Build the normal strace binary and the strace-log-merge helper script;
  the test suite is not built or run.
