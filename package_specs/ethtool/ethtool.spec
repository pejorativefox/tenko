Name:       ethtool
Version:    7.2
Release:    1
Summary:    Settings tool for Ethernet NICs
License:    GPL-2.0-only AND GPL-2.0-or-later
URL:        https://www.kernel.org/pub/software/network/ethtool/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr
BuildRequires: libmnl
BuildRequires: pkgconf
BuildRequires: bash-completion

%description
ethtool is a utility for displaying and changing Ethernet device settings,
including link speed, duplex, offloads, ring sizes, coalescing, channels,
statistics and EEE.  It is used by TuneD's net plugin and by several TuneD
profiles.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/ethtool.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 7.2-1
- New package: ethtool 7.2 (latest stable upstream).  Not in the base set;
  TuneD requires it and the net plugin uses it to apply Ethernet settings.
  The netlink interface is enabled through the newly packaged libmnl.
