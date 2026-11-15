Name:       python3-distro
Version:    1.9.0
Release:    1
Summary:    Linux OS platform information API for Python
License:    Apache-2.0
URL:        https://github.com/python-distro/distro
Source0:    distro-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch

BuildRequires: python-setuptools

%description
distro provides information about the Linux distribution it runs on
(id, name, version, codename) from os-release and related files.

%prep
%setup -q -n distro-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-distro.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 1.9.0-1
- New package, not in the base set: latest upstream stable release
  (1.9.0, checked 2026-11-15); needed by auto-cpufreq.
