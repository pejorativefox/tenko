Name:       python3-psutil
Version:    7.2.2
Release:    1
Summary:    Process and system utilization library for Python
License:    BSD-3-Clause
URL:        https://github.com/giampaolo/psutil
Source0:    psutil-%{version}.tar.gz
Prefix:     /usr

BuildRequires: python-setuptools

%description
psutil retrieves information on running processes and system utilization
(CPU, memory, disks, network, sensors) from Python.

%prep
%setup -q -n psutil-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-psutil.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 7.2.2-1
- New package, not in the base set: latest upstream stable release
  (7.2.2, checked 2026-11-15); needed by auto-cpufreq.
