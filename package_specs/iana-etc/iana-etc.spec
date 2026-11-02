Name:       iana-etc
Version:    20261015
Release:    1
Summary:    Authoritative list of internet protocals
License:    GPL3
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Protocol parameter registries represent the authoritative record of many of the codes and numbers contained in a variety of Internet protocols.

%prep
%setup -q -a0

%build

%install    
rm -rf %{buildroot}
mkdir -pv %{buildroot}/etc
cp services protocols %{buildroot}/etc

%files
/etc/protocols
/etc/services

%changelog
* Mon Nov  2 2026 browneye <build@browneye.invalid> 20261015-1
- Update to 20261015 (current LFS/BLFS r13.1 trunk version).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 20260805
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 20230810
- Version bump
