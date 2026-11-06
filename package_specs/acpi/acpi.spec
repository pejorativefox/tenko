Name:       acpi
Version:    1.8
Release:    2
Summary:    Client for battery, power, and thermal readings
License:    GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
Client for battery, power, and thermal readings.

%prep
%setup -q -n %{name}-%{version}

%build
%configure
%make_build

%install
rm -rf %{buildroot}
install -Dm755 acpi %{buildroot}%{_bindir}/acpi
install -Dm644 acpi.1 %{buildroot}%{_mandir}/man1/acpi.1

%files -f %{_sourcedir}/acpi.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.8-2
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING and the acpi.c/acpi.h headers (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.8-1
- Not in the base set; 1.8 is the latest upstream stable (2025).
- Build 1.8 instead of the earlier 1.7 target.
- Install the binary and man page manually; refresh %files from the
  build.
