Name:       python-jinja
Version:    3.1.6
Release:    4
Summary:    Python templating language
License:    Custom
Source0:    jinja2-3.1.6.tar.gz
Prefix:     /usr
BuildRequires: python-flit-core
Requires: python-markupsafe

%description
Jinja is a modern and designer-friendly templating language for Python, modelled after Django’s templates.

%prep
%setup -n jinja2-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python-jinja.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 3.1.6-4
- Rebuild with tenko-rpm-config 6-4: python(abi) = 3.15 is generated, so drop the explicit Requires: python.

* Wed Nov 11 2026 tenko <build@tenko.invalid> 3.1.6-3
- Require python and python-markupsafe: jinja2 imports markupsafe, and the package shipped without any runtime requirement (no Python dependency generator).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 3.1.6-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 3 paths updated.

* Fri Oct 30 2026 browneye <build@browneye.invalid> 3.1.6
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 3.1.2-1
- Version bump

* Sun May 24 2020 Chris Statzer <chris.statzer@qq.com> 2.11.2
- Initial rpm package
