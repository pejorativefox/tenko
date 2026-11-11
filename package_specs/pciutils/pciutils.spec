Name:       pciutils
Version:    3.15.0
Release:    3
Summary:    The PCI Utilities
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
The PCI Utilities

%prep
%setup

%build
%make_build PREFIX=/usr SHARED=yes LIBDIR=%{_libdir}

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} PREFIX=/usr SHARED=yes LIBDIR=%{_libdir} \
    install install-lib

%files -f %{_sourcedir}/pciutils.filelist

%changelog
* Wed Nov 11 2026 browneye <build@browneye.invalid> 3.15.0-3
- Build and ship the shared libpci library, its headers and libpci.pc in
  the runtime package (no -devel subpackage).  PowerTOP uses libpci for
  its PCI device power information.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.15.0-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): README (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 3.15.0-1
- Sync with the base set

* Mon May 18 2020 Chris Statzer <chris.statzer@qq.com> 3.6.4
- Initial RPM

