Name:       numactl
Version:    2.0.19
Release:    2
Summary:    Library and tools for NUMA policy control
License:    GPL-2.0-only AND LGPL-2.1-only
URL:        https://github.com/numactl/numactl
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

# BuildRequires: none (toolchain only)

%description
numactl provides libnuma plus the numactl, numastat, numademo,
migratepages, migspeed and memhog tools for querying and setting the
NUMA policy of processes and shared memory.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir* %{buildroot}%{_libdir}/libnuma.la
# The kernel syscall manual belongs to man-pages, not the libnuma tools.
rm -f %{buildroot}%{_mandir}/man2/move_pages.2 \
    %{buildroot}%{_mandir}/man2/move_pages.2.gz

%files -f %{_sourcedir}/numactl.filelist

%changelog
* Tue Nov 24 2026 tenko <build@tenko.invalid> 2.0.19-2
- Exclude move_pages(2), which man-pages owns, so numactl and the Java 21
  package recommending it can install on systems with man-pages.
- Regenerate the static filelist without shared-directory ownership.
- Retain 2.0.19, the latest upstream stable release checked 2026-11-24.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.0.19-1
- Update 2.0.12 -> 2.0.19: not in the base set; latest upstream
  stable 2026-11-05 (https://github.com/numactl/numactl/releases).
- Build with --disable-static (as before) and drop the libtool
  libnuma.la archive from the package.
