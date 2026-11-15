Name:       python3-poetry-core
Version:    2.5.0
Release:    1
Summary:    Poetry PEP 517 build backend
License:    MIT AND BSD-3-Clause AND (Apache-2.0 OR BSD-2-Clause)
URL:        https://github.com/python-poetry/poetry-core
Source0:    poetry_core-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch

BuildRequires: python

%description
poetry-core is the PEP 517 build backend used by Poetry projects.  It builds
wheels from a pyproject.toml without Poetry itself.  Its own dependencies
(fastjsonschema, lark, packaging, tomli) are vendored.

%prep
%setup -q -n poetry_core-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-poetry-core.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 2.5.0-1
- New package, not in the base set: latest upstream stable release
  (2.5.0, checked 2026-11-15); the build backend for auto-cpufreq.
