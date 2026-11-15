Name:       python3-click
Version:    8.5.1
Release:    1
Summary:    Composable command line interface toolkit for Python
License:    BSD-3-Clause
URL:        https://palletsprojects.com/projects/click/
Source0:    click-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch

BuildRequires: python-flit-core

%description
Click is a Python package for creating command line interfaces with as
little code as necessary.

%prep
%setup -q -n click-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-click.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 8.5.1-1
- New package, not in the base set: latest upstream stable release
  (8.5.1, checked 2026-11-15); needed by auto-cpufreq.
