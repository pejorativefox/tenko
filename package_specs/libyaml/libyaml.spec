Name:       libyaml
Version:    0.2.5
Release:    3
Summary:    YAML 1.1 parser and emitter written in C
License:    MIT
URL:        https://pyyaml.org/wiki/LibYAML
Prefix:     /usr
Source0:    yaml-%{version}.tar.gz

%description
LibYAML is a YAML 1.1 parser and emitter written in C.

%prep
%setup -q -n yaml-%{version}

%build
%configure --disable-static
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libyaml.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.2.5-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.2.5-1
- Update to the pinned version (0.2.5, was 0.2.1) for the E1
  dnf/libdnf dependency chain (libmodulemd and libdnf).
- Renamed the package/spec directory from yaml to libyaml to match the
  upstream name.
- Use a generated static filelist.
