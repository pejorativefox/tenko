Name:       python-wheel
Version:    0.48.0
Release:    3
Summary:    The official binary distribution format for Python 
License:    MIT
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
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python-wheel.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.48.0-3
- Replace the legacy short licence name with the verified SPDX expression
  (MIT): LICENSE.txt (issue #8).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.48.0-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 2 paths updated.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.48.0
- Replace directory globs with a generated static filelist

* Fri Oct 30 2026 browneye <build@browneye.invalid> 0.48.0
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 0.41.1
- Version bump

* Tue Dec 11 2019 Chris Statzer <chris.statzer@qq.com> 0.33.6
- Initial rpm package
