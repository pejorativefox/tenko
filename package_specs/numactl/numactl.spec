Name:       numactl
Version:    2.0.19
Release:    1
Summary:    Library and tools for NUMA policy control
License:    GPL-2.0-only AND LGPL-2.1-only
URL:        https://github.com/numactl/numactl
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

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

%files -f %{_sourcedir}/numactl.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.0.19-1
- Update 2.0.12 -> 2.0.19: not in the base set; latest upstream
  stable 2026-11-05 (https://github.com/numactl/numactl/releases).
- Build with --disable-static (as before) and drop the libtool
  libnuma.la archive from the package.
