Name:       python-flit-core
Version:    4.2.0
Release:    1
Summary:    Python packaging utility (core)
License:    BSD
Source0:    flit_core-%{version}.tar.gz
Prefix:     /usr

%description
Flit is a simple way to put Python packages and modules on PyPI. 

%prep
%setup -n flit_core-%{version}

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
* Tue Nov 03 2026 browneye <build@browneye.invalid> 4.2.0-1
- Sync with LFS r13.1

* Mon Nov 02 2026 browneye <build@browneye.invalid> 4.0.2-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 3 paths updated.

* Fri Oct 30 2026 browneye <build@browneye.invalid> 4.0.2
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Initial RPM

