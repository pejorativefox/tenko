Name:       tenko-rpm-config
Version:    6
Release:    4
Epoch:      1
Summary:    RPM build macros for Tenko packages
License:    MIT
Prefix:     /usr

Requires: rpm
Requires: binutils
Requires: file

%description
RPM macros and library paths used to build Tenko packages inside the base
container, and the Python dependency generator: files under
/usr/lib*/pythonX.Y/ require python(abi) = X.Y, which the interpreter
provides.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_rpmmacrodir}
install -m 644 %{_sourcedir}/macros.tenko %{buildroot}%{_rpmmacrodir}/macros.tenko
install -D -m 644 %{_sourcedir}/python.attr %{buildroot}%{_fileattrsdir}/python.attr
install -D -m 755 %{_sourcedir}/tenko-pythondeps.sh %{buildroot}%{_rpmconfigdir}/tenko-pythondeps.sh

%files -f %{_sourcedir}/tenko-rpm-config.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 6-4
- Add a python(abi) dependency generator (fileattrs/python.attr and
  tenko-pythondeps.sh): files under /usr/lib*/pythonX.Y/ require
  python(abi) = X.Y and /usr/bin/pythonX.Y provides it.  Module packages
  shipped without any requirement on the interpreter.

* Mon Nov 09 2026 tenko <build@tenko.invalid> 6-3
- Drop the vendored strip helper and the %strip / %__spec_install_post
  overrides.  rpm's platform macros load after macros.tenko and already
  replace %__spec_install_post, so the override never ran; stripping is
  handled by brp-strip inside %__os_install_post.

* Mon Nov 09 2026 browneye <build@browneye.invalid> 6-2
- Align %_dbpath with installed systems: /var/lib/rpm instead of
  /usr/lib/sysimage/rpm.  tenko-osdev/tenko-base-build install this macro
  package on running systems, and the old path made rpm/dnf lose the
  existing database after installation.  Images built before this release
  need a one-time database move or a rebuild.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 6-1
- Rebase on the Tenko 6 distro release with Epoch 1 so installs carrying
  the old 13.1 EVR upgrade cleanly.
- Drop the browneye-rpm-config Obsoletes/Provides alias and the old macro
  cleanup; no Browneye installs remain.

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
