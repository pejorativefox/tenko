Name:       lsof
Version:    4.99.7
Release:    1
Summary:    Lists open files and the processes that opened them
License:    lsof
URL:        https://github.com/lsof-org/lsof
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: libtirpc
BuildRequires: groff

%description
lsof (list open files) reports information about files opened by processes:
regular files, directories, memory-mapped files, sockets, pipes and devices.
For each open file it shows the process name and PID, the user, the file
descriptor and access mode, and the file's type, device, size and path.  This
makes lsof useful for finding which process holds a busy mount point, which
program kept a socket or port open, and which deleted files still occupy disk
space.

%prep
%setup -q

%build
# Build only the command-line tool: this distro has no -devel packages, so
# the optional liblsof library (headers, .pc and unversioned .so) is skipped.
%configure --disable-liblsof
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/lsof.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 4.99.7-1
- Initial package at the latest stable upstream release, lsof 4.99.7
  (published 2026-06-16), from the upstream release tarball.
- Licence verified as the lsof licence (SPDX: lsof) from COPYING, which
  matches the SPDX lsof licence text.
- Build with upstream's autotools configure script (4.99 switched from
  the old ./Configure entry point) and --disable-liblsof; install the
  lsof binary and its man page.
