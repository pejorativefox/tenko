Name:       python3-pyudev
Version:    0.24.5
Release:    1
Summary:    Python libudev binding
License:    LGPL-2.1-or-later
URL:        https://github.com/pyudev/pyudev
Source0:    pyudev-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch
BuildRequires: python-setuptools
BuildRequires: python-wheel
Requires:   systemd

%description
pyudev is a pure-Python binding for libudev.  It provides access to udev
device enumeration, monitoring and attributes.  TuneD uses it to build its
hardware inventory and to match devices for the net, disk and other plugins.

%prep
%setup -q -n pyudev-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-pyudev.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 0.24.5-1
- New package: pyudev 0.24.5 (latest stable upstream).  Not in the base
  set; TuneD imports pyudev from its daemon, hardware inventory and net
  plugin.
