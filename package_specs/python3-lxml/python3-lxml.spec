Name:       python3-lxml
Version:    6.1.3
Release:    3
Summary:    Python bindings for libxml2 and libxslt
License:    BSD-3-Clause AND PSF-2.0 AND MIT
Source0:    lxml-%{version}.tar.gz
Prefix:     /usr

%description
lxml provides Python bindings for libxml2 and libxslt.  itstool uses it in
place of the removed libxml2 Python module.

%prep
%setup -q -n lxml-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-lxml.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 6.1.3-3
- Rebuild with tenko-rpm-config 6-4 for the generated python(abi) = 3.15 requirement on its Python modules.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 6.1.3-2
- Replace the legacy short licence name with the verified SPDX expression
  (BSD-3-Clause AND PSF-2.0 AND MIT): LICENSE.txt (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 6.1.3-1
- New package, synced with the base set.  itstool needs lxml because libxml2
  no longer ships its Python bindings.
