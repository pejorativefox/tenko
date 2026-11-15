Name:       python3-pyasyncore
Version:    1.0.5
Release:    1
Summary:    The asyncore module for Python 3.12 and later
License:    PSF-2.0
URL:        https://github.com/simonrob/pyasyncore
Source0:    pyasyncore-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch

BuildRequires: python-setuptools

%description
pyasyncore makes the asyncore module, removed from the standard library in
Python 3.12, available again for code that still imports it.

%prep
%setup -q -n pyasyncore-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-pyasyncore.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 1.0.5-1
- New package, not in the base set: latest upstream stable release
  (1.0.5, checked 2026-11-15); needed by pyinotify.
