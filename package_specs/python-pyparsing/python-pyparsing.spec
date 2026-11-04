Name:       python-pyparsing
Version:    3.3.3
Release:    1
Summary:    Python module for creating parsers
License:    MIT
Source0:    pyparsing-%{version}.tar.gz
Prefix:     /usr

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
* Wed Nov 04 2026 browneye <build@browneye.invalid> 3.3.3-1
- Update from 2.4.5 to 3.3.3, synced with BLFS r13.1.  Flatpak 1.18.4
  requires the pyparsing module at build time.
