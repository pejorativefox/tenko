Name:       pciutils
Version:    3.15.0
Release:    1
Summary:    The PCI Utilities
License:    GPL
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The PCI Utilities

%prep
%setup

%build
%make_build PREFIX=/usr

%install
rm -rf %{buildroot}
%make_install PREFIX=/usr

%files
/usr/bin/lspci
/usr/sbin/pcilmr
/usr/sbin/setpci
/usr/sbin/update-pciids
/usr/share/man/man5/pci.ids.5.gz
/usr/share/man/man7/pcilib.7.gz
/usr/share/man/man8/lspci.8.gz
/usr/share/man/man8/pcilmr.8.gz
/usr/share/man/man8/setpci.8.gz
/usr/share/man/man8/update-pciids.8.gz
/usr/share/pci.ids.gz

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.15.0-1
- Sync with BLFS r13.1

* Mon May 18 2020 Chris Statzer <chris.statzer@qq.com> 3.6.4
- Initial RPM

