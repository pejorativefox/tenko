Name:       python3-pyinotify
Version:    0.9.6
Release:    1
Summary:    Linux filesystem events monitoring for Python
License:    MIT
URL:        https://github.com/seb-m/pyinotify
Source0:    pyinotify-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch

BuildRequires: python-setuptools
Requires:   python3-pyasyncore

%description
pyinotify monitors filesystem events through the Linux inotify interface.

%prep
%setup -q -n pyinotify-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-pyinotify.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 0.9.6-1
- New package, not in the base set: latest upstream stable release
  (0.9.6, checked 2026-11-15); needed by auto-cpufreq.
