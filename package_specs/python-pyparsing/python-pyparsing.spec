Name:       python-pyparsing
Version:    3.3.3
Release:    3
Summary:    Python module for creating parsers
License:    MIT
Source0:    pyparsing-%{version}.tar.gz
Prefix:     /usr
BuildRequires: python-flit-core

%description
pyparsing is a general parsing module for Python.  Flatpak's build uses it
for its metadata and schema tooling.

%prep
%setup -q -n pyparsing-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python-pyparsing.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 3.3.3-3
- Rebuild with tenko-rpm-config 6-4: python(abi) = 3.15 is generated, so drop the explicit Requires: python.

* Wed Nov 11 2026 tenko <build@tenko.invalid> 3.3.3-2
- Require python: Tenko has no Python dependency generator, so the module package shipped without any runtime requirement.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 3.3.3-1
- Update from 2.4.5 to 3.3.3, synced with the base set.  Flatpak 1.18.4
  requires the pyparsing module at build time.
