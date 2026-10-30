Name:       python-wheel
Version:    0.48.0
Release:    1
Summary:    The official binary distribution format for Python 
License:    GPL
Source0:    wheel-%{version}.tar.gz
Prefix:     /usr

%description
The official binary distribution format for Python 

%prep
%setup -n wheel-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.14 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.14 %{buildroot}/usr/lib64/
fi

%files
/usr/bin/
/usr/lib64/python3.14/site-packages/

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 0.48.0
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 0.41.1
- Version bump

* Tue Dec 11 2019 Chris Statzer <chris.statzer@qq.com> 0.33.6
- Initial rpm package
