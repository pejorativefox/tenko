Name:       stunnel 
Version:    5.82
Release:    2
Summary:    TLS proxy daemon.
License:    GPL-2.0-or-later WITH stunnel-exception
URL:        https://www.stunnel.org/
Source0:    %{name}-%{version}.tar.gz
Source1:    stunnel-service.conf
Source2:    stunnel.service
Prefix:     /usr
BuildRequires: openssl

%description
Stunnel is a proxy designed to add TLS encryption functionality to existing clients and servers without any changes in the programs' code. 

%prep
%setup -n stunnel-%{version}

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

mkdir -pv %{buildroot}/etc/finit.d/available
mkdir -pv %{buildroot}/etc/service.d

cp %{SOURCE1} %{buildroot}/etc/finit.d/available/stunnel.conf
cp %{SOURCE2} %{buildroot}/etc/service.d/


%files -f %{_sourcedir}/stunnel.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 5.82-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later WITH stunnel-exception): COPYING.md (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 5.82-1
- Sync with the base set

* Mon Jun 12 2023 Chris Statzer <chris.statzer@gmail.com> 5.69
- Version bump

* Thu May 14 2020 Chris Statzer <chris.statzer@qq.com> 5.56-2
- Added finit control script

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 5.56
- Initial package.
