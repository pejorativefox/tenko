Name:       s-tui
Version:    1.5.0
Release:    1
Summary:    Terminal UI for monitoring CPU temperature, frequency, power and utilization
License:    GPL-2.0-only
URL:        https://github.com/amanusk/s-tui
Source0:    s_tui-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch

BuildRequires: python-setuptools
Requires:   python3-psutil
Requires:   python3-urwid

%description
s-tui is a terminal UI for monitoring CPU temperature, frequency, power
and utilization, showing performance dips caused by thermal throttling.
It runs without an X server and includes a built-in CPU stress test that
works without extra dependencies.

Optional integrations are not packaged: the numpy extra (a BLAS-based
built-in stresser) and the external stress and stress-ng tools.  Without
numpy the built-in stresser falls back to SHA-256 hashing, which still
provides good CPU load.

s-tui is not part of the base set; the user requested the package.

Version 1.5.0 is the latest upstream stable release (PyPI 1.5.0,
published 2026-08-19, checked 2026-11-20).

%prep
# The sdist's top directory uses the PyPI project name (s_tui), not s-tui.
%setup -q -n s_tui-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi
install -Dm644 README.md %{buildroot}%{_docdir}/%{name}/README.md

%files -f %{_sourcedir}/%{name}.filelist

%changelog
* Fri Nov 20 2026 tenko <build@tenko.invalid> 1.5.0-1
- New package, not in the base set: latest upstream stable release
  (1.5.0, PyPI 2026-08-19, checked 2026-11-20).  Installed from the
  sdist with pip (setuptools backend); runs against python3-urwid
  5.1.3 and python3-psutil 7.2.2.  The optional numpy stress extra and
  the external stress/stress-ng tools are not packaged.
