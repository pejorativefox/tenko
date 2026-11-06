Name:       tenko-rpm-config
Version:    13.1
Release:    3
# Tenko rename compatibility (issue #22).
Obsoletes: browneye-rpm-config < 13.1-3
Provides: browneye-rpm-config = %{version}-%{release}
Summary:    RPM macros and strip helper for Tenko builds
License:    MIT
Prefix:     /usr

Requires: rpm
Requires: binutils
Requires: file

%description
RPM macros, library paths, and the strip helper used to build Tenko
packages inside the base container.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_rpmmacrodir} %{buildroot}/usr/lib/rpm/tenko
install -m 644 %{_sourcedir}/macros.tenko %{buildroot}%{_rpmmacrodir}/macros.tenko
install -m 755 %{_sourcedir}/strip_debug.sh %{buildroot}/usr/lib/rpm/tenko/strip_debug.sh

%post
# Remove the old RPM macro directory and macro file.
rm -f /usr/lib/rpm/macros.d/macros.browneye
rm -rf /usr/lib/rpm/browneye

%files
%{_rpmmacrodir}/macros.tenko
/usr/lib/rpm/tenko/strip_debug.sh

%changelog
* Fri Nov 06 2026 tenko <build@tenko.invalid> 13.1-3
- Rename browneye-rpm-config to tenko-rpm-config and add versioned
  Obsoletes/Provides aliases for the Tenko 13.1 compatibility window.
- Clean up old browneye paths, units, presets and configuration.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 13.1-2
- Exclude .pc files from automatic Requires generation.  The development
  payload now ships in the runtime packages, and their pkgconfig(...)
  Requires were pulling mesa, libdrm and other build-time dependencies
  into the desktop closure (issue #4).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 13.1
- RPM build configuration for the base container
