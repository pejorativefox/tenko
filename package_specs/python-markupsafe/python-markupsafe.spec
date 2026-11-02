Name:       python-markupsafe
Version:    3.0.3
Release:    2
Summary:    Safely add untrusted strings to HTML/XML markup.
License:    BSD
Source0:    markupsafe-3.0.3.tar.gz
Prefix:     /usr

%description
Safely add untrusted strings to HTML/XML markup.

%prep
%setup -n markupsafe-%{version}

%build

%install
rm -rf %{buildroot}
MARKUPSAFE_PURE_PYTHON=1 python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files
/usr/lib64/python3.15/site-packages/

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.0.3-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 3 paths updated.

* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.0.3
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 
- Version bump

* Sun May 24 2020 Chris Statzer <chris.statzer@qq.com> 1.1.1-1
- Initial rpm package
