Name:       libyaml
Version:    0.2.5
Release:    1
Summary:    YAML 1.1 parser and emitter written in C
License:    MIT
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
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.2.5-1
- Update to the BLFS r13.1 version (0.2.5, was 0.2.1) for the E1
  dnf/libdnf dependency chain (libmodulemd and libdnf).
- Renamed the package/spec directory from yaml to libyaml to match the
  upstream and BLFS name.
- Use a generated static filelist.
