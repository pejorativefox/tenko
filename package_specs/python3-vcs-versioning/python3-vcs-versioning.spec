Name:       python3-vcs-versioning
Version:    2.6.0
Release:    1
Summary:    Version numbers from version control metadata
License:    MIT
URL:        https://github.com/pypa/setuptools-scm
Source0:    vcs_versioning-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch

BuildRequires: python-packaging
BuildRequires: python-setuptools
Requires:   python-packaging

%description
vcs-versioning computes package versions from git and mercurial metadata.
It is the core library behind setuptools-scm.

%prep
%setup -q -n vcs_versioning-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-vcs-versioning.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 2.6.0-1
- New package, not in the base set: latest upstream stable release
  (2.6.0, checked 2026-11-15); needed by setuptools-scm.
