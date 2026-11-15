Name:       python3-setuptools-scm
Version:    10.3.4
Release:    1
Summary:    Setuptools plugin that manages versions from SCM tags
License:    MIT
URL:        https://github.com/pypa/setuptools-scm
Source0:    setuptools_scm-%{version}.tar.gz
Prefix:     /usr
BuildArch:  noarch

BuildRequires: python-packaging
BuildRequires: python-setuptools
BuildRequires: python3-vcs-versioning
Requires:   python-packaging
Requires:   python-setuptools
Requires:   python3-vcs-versioning

%description
setuptools-scm extracts package versions from git or mercurial metadata
for setuptools builds.

%prep
%setup -q -n setuptools_scm-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-setuptools-scm.filelist

%changelog
* Sun Nov 15 2026 tenko <build@tenko.invalid> 10.3.4-1
- New package, not in the base set: latest upstream stable release
  (10.3.4, checked 2026-11-15); build backend plugin for urwid.
