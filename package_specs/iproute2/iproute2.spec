Name:       iproute2
Version:    7.3.0
Release:    2
Summary:    kernel networking tool
License:    GPL-2.0-or-later
URL:        https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/
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

%files -f %{_sourcedir}/iproute2.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 7.3.0-2
- Record the verified license (GPL-2.0-or-later): ip/ip.c (SPDX header) and COPYING (issue #8).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 7.3.0-1
- Update to 7.3.0 (current upstream version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 7.2.0-2
- Rebuild against the base libtirpc (size audit P0); no host library

* Fri Oct 30 2026 browneye <build@browneye.invalid> 7.1.0
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 6.4.0-1
- Version bump
