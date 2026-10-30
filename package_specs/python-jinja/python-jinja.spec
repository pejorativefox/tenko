Name:       python-jinja
Version:    3.1.6
Release:    1
Summary:    Python templating language
License:    Custom
Source0:    jinja2-3.1.6.tar.gz
Prefix:     /usr

%description
Jinja is a modern and designer-friendly templating language for Python, modelled after Django’s templates.

%prep
%setup -n jinja2-%{version}

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
* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.1.6
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 3.1.2-1
- Version bump

* Sun May 24 2020 Chris Statzer <chris.statzer@qq.com> 2.11.2
- Initial rpm package
