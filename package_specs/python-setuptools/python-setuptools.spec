Name:       python-setuptools
Version:    84.0.0
Release:    1
Summary:    Python setuptools build system.
License:    LGPL
Source0:    setuptools-%{version}.tar.gz
Prefix:     /usr

%description
Python setuptools build system. 

%prep
%setup -n setuptools-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.14 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.14 %{buildroot}/usr/lib64/
fi

%files
/usr/lib64/python3.14/site-packages/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 84.0.0
- Sync with LFS r13.1

* Tue Dec 11 2019 Chris Statzer <chris.statzer@qq.com> 42.0.2
- Initial rpm package
