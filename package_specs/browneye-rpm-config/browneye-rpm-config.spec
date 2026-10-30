Name:       browneye-rpm-config
Version:    13.1
Release:    1
Summary:    RPM macros and strip helper for Browneye builds
License:    MIT
Prefix:     /usr

Requires: rpm
Requires: binutils
Requires: file

%description
RPM macros, library paths, and the strip helper used to build Browneye
packages inside the base container.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_rpmmacrodir} %{buildroot}/usr/lib/rpm/browneye
install -m 644 %{_sourcedir}/macros.browneye %{buildroot}%{_rpmmacrodir}/macros.browneye
install -m 755 %{_sourcedir}/strip_debug.sh %{buildroot}/usr/lib/rpm/browneye/strip_debug.sh

%files
%{_rpmmacrodir}/macros.browneye
/usr/lib/rpm/browneye/strip_debug.sh

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 13.1
- RPM build configuration for the base container
