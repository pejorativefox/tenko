Name:       python-packaging
Version:    26.3
Release:    1
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
if [ -d %{buildroot}/usr/lib/python3.14 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.14 %{buildroot}/usr/lib64/
fi

%files
/usr/lib64/python3.14/site-packages/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 26.3
- Sync with LFS r13.1

* Tue Dec 11 2019 Chris Statzer <chris.statzer@qq.com> 19.2
- Initial rpm package
