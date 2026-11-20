Name:       btop
Version:    1.4.8
Release:    1
Summary:    Monitor of CPU, memory, disks, network, processes and GPU resources
License:    Apache-2.0
URL:        https://github.com/aristocratos/btop
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

# BuildRequires: none (toolchain only)

%description
btop is a monitor of system resources: per-core CPU frequency and
utilisation, memory and swap, disks (I/O and utilisation), network
interfaces and a searchable, sortable process list with tree view, filters
and signals.  It renders a full-screen TUI with mouse support and themeable
boxes, and shows GPU utilisation, temperature, power draw and VRAM for
NVIDIA, AMD and Intel devices by loading the vendor libraries (NVIDIA NVML,
ROCm SMI, Intel Level Zero) with dlopen at runtime.

btop is not part of the base set.

%prep
%setup -q

%build
# The man page is generated from manpage.md only when lowdown is installed;
# the repository does not package lowdown, so btop.1 is deliberately not
# built and not installed.  GPU support is on by default on linux x86_64
# and needs nothing but dlopen at build time.
%make_build PREFIX=/usr

%install
rm -rf %{buildroot}
%make_install PREFIX=/usr

%files -f %{_sourcedir}/btop.filelist

%changelog
* Fri Nov 20 2026 tenko <build@tenko.invalid> 1.4.8-1
- New package, not in the base set: latest upstream stable release
  (1.4.8, checked 2026-11-20).
- GPU monitoring is compiled in; the vendor libraries are dlopen'ed at
  runtime, so there are no build or runtime requirements beyond the
  toolchain.
- The man page is skipped: generating it needs lowdown, which the
  repository does not package.
