Name:       iana-etc
Version:    20261015
Release:    2
Summary:    Authoritative list of internet protocals
License:    MIT
URL:        https://github.com/Mic92/iana-etc
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

%files -f %{_sourcedir}/iana-etc.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 20261015-2
- Record the verified license (MIT): upstream repository LICENSE (tarball ships no license file) (issue #8).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 20261015-1
- Update to 20261015 (current upstream version).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 20260805
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 20230810
- Version bump
