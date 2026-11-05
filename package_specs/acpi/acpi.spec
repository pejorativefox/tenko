Name:       acpi
Version:    1.8
Release:    1
Summary:    Client for battery, power, and thermal readings
License:    GPL2
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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.8-1
- Not in the r13.1 book; 1.8 is the latest upstream stable (2025).
- Build 1.8 instead of the earlier 1.7 target.
- Install the binary and man page manually; refresh %files from the
  build.
