Name:       python-packaging
Version:    26.3
Release:    2
Summary:    Core utilities for Python packages
License:    GPL
Source0:    packaging-%{version}.tar.gz
Prefix:     /usr

%description
Core utilities for Python packages

%prep
%setup -n packaging-%{version}

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
* Mon Nov 02 2026 browneye <build@browneye.invalid> 26.3-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 3 paths updated.

* Fri Oct 30 2026 browneye <build@browneye.invalid> 26.3
- Sync with LFS r13.1

* Tue Dec 11 2019 Chris Statzer <chris.statzer@qq.com> 19.2
- Initial rpm package
