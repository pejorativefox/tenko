Name:       acpica
Version:    20260930
Release:    1
Summary:    ACPI Component Architecture tools
License:    BSD-3-Clause OR GPL-2.0-only
URL:        https://www.acpica.org/
Source0:    acpica-unix-%{version}.tar.gz
Prefix:     /usr

%description
ACPICA is the reference implementation of the ACPI specification.  It
provides the Intel ACPI Source Language compiler (iasl), the disassembler,
and the acpiexec/acpixtract/acpidump/acpibin/acpihelp/acpisrc tools.  The
iasl compiler is required to build firmware images such as EDK2/OVMF.

%prep
%setup -q -n acpica-unix-%{version}

%build
make -C generate/unix %{?_smp_mflags}

%install
rm -rf %{buildroot}
make -C generate/unix install DESTDIR=%{buildroot} PREFIX=/usr

%files
/usr/bin/acpibin
/usr/bin/acpidump
/usr/bin/acpiexamples
/usr/bin/acpiexec
/usr/bin/acpihelp
/usr/bin/acpisrc
/usr/bin/acpixtract
/usr/bin/iasl

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 20260930-1
- Not in the base set; latest upstream release (2026-09-30).
  Needed for the EDK2/OVMF firmware package (iasl).
- License basis: LICENSE.BSD-3-Clause and LICENSE.GPL-2.0-only in the
  tarball; the project is dual-licensed.
