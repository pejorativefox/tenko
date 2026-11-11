Name:       python-pefile
Version:    2024.8.26
Release:    2
Summary:    Python module for reading and writing Portable Executable files
License:    MIT
URL:        https://github.com/erocarrera/pefile
Source0:    pefile-%{version}.tar.gz
BuildRequires: python
BuildRequires: python-setuptools
BuildRequires: python-wheel
Prefix:     /usr
Requires: python

%description
pefile is a pure-Python module for reading and writing Portable Executable
(PE) files.  fwupd-efi uses it at build time to add NX compatibility flags to
the generated UEFI binary when the external genpeimg tool is unavailable.

%prep
%setup -n pefile-%{version}

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python-pefile.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 2024.8.26-2
- Require python: Tenko has no Python dependency generator, so the module package shipped without any runtime requirement.

* Mon Nov 09 2026 browneye <build@browneye.invalid> 2024.8.26-1
- Initial package: latest stable upstream release 2024.8.26.  Build-only
  dependency of fwupd-efi, which needs it to mark the UEFI binary NX.
- Licence verified from LICENSE and the PKG-INFO metadata (MIT).
