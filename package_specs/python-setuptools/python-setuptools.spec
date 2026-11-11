Name:       python-setuptools
Version:    84.2.1
Release:    4
Summary:    Python setuptools build system.
License:    MIT AND LGPL-3.0-or-later AND Apache-2.0
URL:        https://github.com/pypa/setuptools
Source0:    setuptools-%{version}.tar.gz
Prefix:     /usr
%description
Python setuptools build system. 

%prep
%setup -n setuptools-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python-setuptools.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 84.2.1-4
- Rebuild with tenko-rpm-config 6-4: python(abi) = 3.15 is generated, so drop the explicit Requires: python.

* Wed Nov 11 2026 tenko <build@tenko.invalid> 84.2.1-3
- Require python: Tenko has no Python dependency generator, so the module package shipped without any runtime requirement.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 84.2.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (MIT AND LGPL-3.0-or-later AND Apache-2.0): LICENSE (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 84.2.1-1
- Sync with the base set

* Mon Nov 02 2026 browneye <build@browneye.invalid> 84.0.0-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 3 paths updated.

* Fri Oct 30 2026 browneye <build@browneye.invalid> 84.0.0
- Sync with the base set

* Tue Dec 11 2019 Chris Statzer <chris.statzer@qq.com> 42.0.2
- Initial rpm package
