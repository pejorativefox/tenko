Name:       gnupg
Version:    2.5.24
Release:    2
Summary:    GNU's tool for secure communication and data storage.
License:    GPL-3.0-or-later
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

%description
GNU's tool for secure communication and data storage.

%prep
%setup

%build
%configure --enable-symcryptrun     \
           --docdir=/usr/share/doc/gnupg-2.2.9
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -rf %{buildroot}/usr/share/info/dir

%files -f %{_sourcedir}/gnupg.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.5.24-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-3.0-or-later): COPYING and the per-file SPDX headers (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.5.24-1
- Sync with the base set

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 2.2.9
- Initial RPM

