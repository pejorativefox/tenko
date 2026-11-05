Name:       python-setuptools
Version:    84.2.1
Release:    2
Summary:    Python setuptools build system.
License:    MIT AND LGPL-3.0-or-later AND Apache-2.0
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

%files
/usr/lib64/python3.15/site-packages/

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 84.2.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (MIT AND LGPL-3.0-or-later AND Apache-2.0): LICENSE (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 84.2.1-1
- Sync with LFS r13.1

* Mon Nov 02 2026 browneye <build@browneye.invalid> 84.0.0-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 3 paths updated.

* Fri Oct 30 2026 browneye <build@browneye.invalid> 84.0.0
- Sync with LFS r13.1

* Tue Dec 11 2019 Chris Statzer <chris.statzer@qq.com> 42.0.2
- Initial rpm package
