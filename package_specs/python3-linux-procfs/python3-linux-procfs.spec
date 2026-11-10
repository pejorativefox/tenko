Name:       python3-linux-procfs
Version:    0.7.4
Release:    1
Summary:    Linux /proc abstraction classes
License:    GPL-2.0-only
URL:        https://www.kernel.org/pub/software/libs/python/python-linux-procfs
Source0:    python-linux-procfs-%{version}.tar.xz
Prefix:     /usr
BuildArch:  noarch
BuildRequires: python-setuptools
BuildRequires: python-wheel

%description
python-linux-procfs provides the procfs Python package, which abstracts
process and scheduler information from /proc.  TuneD's scheduler plugin and
profile recommender use it to inspect processes and their scheduler
attributes.

%prep
%setup -q -n python-linux-procfs-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-linux-procfs.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 0.7.4-1
- New package: python-linux-procfs 0.7.4 (latest stable upstream).  Not in
  the base set; TuneD's scheduler plugin and profile recommender import
  procfs.
