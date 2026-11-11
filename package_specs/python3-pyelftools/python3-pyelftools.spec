Name:       python3-pyelftools
Version:    0.33
Release:    2
Summary:    Pure-Python library for parsing ELF files and DWARF debugging data
License:    Public Domain
Source0:    pyelftools-%{version}.tar.gz
Prefix:     /usr
BuildRequires: python-setuptools
BuildRequires: python-wheel

%description
pyelftools is a pure-Python library for parsing and analyzing ELF files and
DWARF debugging information.

systemd's meson build uses it to inspect the EFI binaries it produces, so it
is a build-time dependency of the systemd package when the EFI bootloader
(sd-boot) is enabled.  Nothing on a Tenko system requires it at runtime.

%prep
%setup -n pyelftools-%{version}

# The sdist's pyproject.toml points the readme at README.rst, but the tarball
# ships README.md; setuptools fails to build the metadata without this.
sed -i 's/^readme = "README.rst"$/readme = "README.md"/' pyproject.toml

%build

%install
rm -rf %{buildroot}
python3 -m pip install --root=%{buildroot} --prefix=/usr --no-deps \
    --no-build-isolation --ignore-installed --no-warn-script-location .
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%files -f %{_sourcedir}/python3-pyelftools.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 0.33-2
- Rebuild with tenko-rpm-config 6-4 for the generated python(abi) = 3.15 requirement on its Python modules.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.33-1
- New package.  Not in the base set; the base build only lists pyelftools as
  an optional build dependency of systemd.  systemd 262.1 needs it for
  -D bootloader=enabled, which produces systemd-bootx64.efi and the EFI stub.
  Pinned to the current PyPI release, 0.33.
