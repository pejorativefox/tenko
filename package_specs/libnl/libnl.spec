Name:       libnl
Version:    3.12.0
Release:    2
Summary:    Netlink socket libraries for Linux
License:    LGPL-2.1-only
URL:        https://github.com/thom311/libnl
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz


%description
libnl is a collection of libraries for applications that communicate with
the Linux kernel using the netlink protocol. It includes core, route,
generic netlink, netfilter, XFRM and diagnostic libraries together with
command line utilities.

%prep
%setup -a 0

%build
%configure --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libnl.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.12.0-2
- Replace the TODO summary/description and record the verified license
  (LGPL-2.1-only): lib/nl.c (SPDX header) (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.12.0-1
- Sync with the base set

# let's skip this for now

