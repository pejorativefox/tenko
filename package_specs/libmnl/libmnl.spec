Name:       libmnl
Version:    1.0.5
Release:    1
Summary:    Minimalistic netlink communication library
License:    LGPL-2.1-or-later
URL:        https://www.netfilter.org/projects/libmnl/
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
libmnl is a minimalistic user-space library oriented to Netlink developers.
It provides a small set of functions for common Netlink tasks, including
message construction, parsing, validation and attribute handling.

ethtool uses it for its netlink interface.

%prep
%setup -q

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libmnl.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 1.0.5-1
- New package: libmnl 1.0.5 (latest stable upstream).  It is not in the
  base set; ethtool's netlink interface needs it, so the library is
  packaged as a runtime dependency.
