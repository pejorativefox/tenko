Name:       libevent
Version:    2.1.13
Release:    2
Summary:    Provides callback functions for file descriptors.
License:    BSD-3-Clause
Source0:    %{name}-%{version}-stable.tar.gz
Prefix:     /usr

%description
The libevent API provides a mechanism to execute a callback function when a specific event occurs on a file descriptor.

%prep
%setup -n %{name}-%{version}-stable

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

%files -f %{_sourcedir}/libevent.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.1.13-2
- Replace the legacy short licence name with the verified SPDX expression
  (BSD-3-Clause): LICENSE, 3-clause BSD (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.1.13-1
- Sync with the base set

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 2.1.12
- Initial RPM

