Name:       acpi
Version:    1.7
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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.7-1
- Not in the r13.1 book; latest upstream stable per the 2026-11-05
  wave target (1.7, 2013). Upstream also publishes 1.8 (2025); that
  version still needs approval, so this build stays at the requested
  1.7.
- Install the binary and man page manually; refresh %files from the
  build.
