Name:       python-pyyaml
Version:    6.0.3
Release:    2
Summary:    Python YAML parser and emitter
License:    MIT
Prefix:     /usr
Source0:    pyyaml-6.0.3.tar.gz
Requires: python
BuildRequires: python-setuptools

%description
PyYAML is a YAML 1.1 parser and emitter for Python.  Mesa's build requires
the yaml module when it reads its configuration files.

The package is built without the optional libyaml C extension so it has no
Cython build dependency; the pure-Python loader is enough for Mesa's
build-time configuration parsing.

%prep
%setup -q -n pyyaml-6.0.3

%build

%install
rm -rf %{buildroot}
PYYAML_FORCE_LIBYAML=0 python3 -m pip install --root=%{buildroot} --prefix=/usr \
    --no-deps --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files
/usr/lib64/python3.15/site-packages/

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 6.0.3-2
- Require python: Tenko has no Python dependency generator, so the module package shipped without any runtime requirement.

* Sun Nov 08 2026 browneye <build@browneye.invalid> 6.0.3-1
- Initial package: PyYAML 6.0.3, the latest stable upstream release.  Mesa's
  meson build requires the yaml module when it reads its configuration files
  (issue #51).
- Build the pure-Python distribution (PYYAML_FORCE_LIBYAML=0): the sdist has
  no generated C source, so the libyaml extension would need Cython, which
  the build image does not ship.
