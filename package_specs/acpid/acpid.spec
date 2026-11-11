Name:       acpid
Version:    2.0.34
Release:    2
Summary:    The acpid (Advanced Configuration and Power Interface event daemon)
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Source1:    lidclose
Source2:    brightnessup
Source3:    brightnessdown
Source4:    acpid.conf
Prefix:     /usr

%description
The acpid (Advanced Configuration and Power Interface event daemon)

%prep
%setup

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install

mkdir -pv %{buildroot}/etc/acpi/events
cp %{SOURCE1} %{buildroot}/etc/acpi/events
cp %{SOURCE2} %{buildroot}/etc/acpi/events
cp %{SOURCE3} %{buildroot}/etc/acpi/events

mkdir -pv %{buildroot}/etc/finit.d/available
cp %{SOURCE4} %{buildroot}/etc/finit.d/available/

%files -f %{_sourcedir}/acpid.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.0.34-2
- Replace NO_IDEA with the verified license (GPL-2.0-or-later): COPYING + acpid.c "either version 2 ... or any later version" (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.0.34-1
- Sync with the base set

* Mon May 18 2020 Chris Statzer <chris.statzer@qq.com> 2.0.28-3
- Added basic events and finit service

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 2.0.28-1
- Initial RPM

