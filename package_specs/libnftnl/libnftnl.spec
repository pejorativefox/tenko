Name:       libnftnl
Version:    1.3.2
Release:    1
Summary:    Library for the nf_tables netlink interface
License:    GPL-2.0-or-later
URL:        https://www.netfilter.org/projects/libnftnl/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: libmnl

%description
libnftnl is a userspace library providing a low-level netlink programming
interface to the in-kernel nf_tables subsystem.  nftables (the nft command)
is built on it.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libnftnl.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 1.3.2-1
- New package, not in the base set: latest upstream stable release
  (1.3.2, checked 2026-11-15).  Needed by nftables (issue #68).
