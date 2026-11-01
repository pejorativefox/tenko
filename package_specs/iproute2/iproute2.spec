Name:       iproute2
Version:    7.2.0
Release:    2
Summary:    kernel networking tool
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
iproute2 is a collection of userspace utilities for controlling and monitoring various aspects of networking in the Linux kernel

%prep
%setup -q

%build
./configure
sed -i "/selinux/Id" config.mk
sed -i /ARPD/d Makefile
rm -fv man/man8/arpd.8
%make_build NETNS_RUN_DIR=/run/netns

%install
rm -rf %{buildroot}
%make_install SBINDIR=/usr/sbin
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/share/iproute2/bpf_pinning
/usr/share/iproute2/ematch_map
/usr/share/iproute2/group
/usr/share/iproute2/nl_protos
/usr/share/iproute2/rt_dsfield
/usr/share/iproute2/rt_protos
/usr/share/iproute2/rt_realms
/usr/share/iproute2/rt_scopes
/usr/share/iproute2/rt_tables
/usr/sbin/bridge
/usr/sbin/ctstat
/usr/sbin/genl
/usr/sbin/ifstat
/usr/sbin/ip
/usr/sbin/lnstat
/usr/sbin/nstat
/usr/sbin/routel
/usr/sbin/rtacct
/usr/sbin/rtmon
/usr/sbin/rtstat
/usr/sbin/ss
/usr/sbin/tc
/usr/lib/tc/
/usr/share/bash-completion/completions/dpll
/usr/lib/tc/pareto.dist
/usr/lib/tc/paretonormal.dist
/usr/share/bash-completion/completions/devlink
/usr/include/iproute2/bpf_elf.h
/usr/share/bash-completion/completions/tc
/usr/share/man/

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 7.2.0-2
- Rebuild against the base libtirpc (size audit P0); no host library

* Fri Oct 30 2026 browneye <build@browneye.invalid> 7.1.0
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 6.4.0-1
- Version bump
