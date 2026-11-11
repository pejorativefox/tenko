Name:       meson
Version:    1.12.1
Release:    4
Summary:    Meson build system
License:    Apache-2.0
URL:        https://mesonbuild.com/
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr
BuildRequires: python-setuptools

%description
Meson build system

%prep
%setup -q

%build
python3 setup.py build

%install
rm -rf %{buildroot}
python3 setup.py install --root=dest
mkdir -pv %{buildroot}/usr
cp -rv dest/* %{buildroot}
mv %{buildroot}/usr/lib %{buildroot}/usr/lib64
install -D -m644 data/shell-completions/bash/meson \
    %{buildroot}/usr/share/bash-completion/completions/meson
install -D -m644 data/shell-completions/zsh/_meson \
    %{buildroot}/usr/share/zsh/site-functions/_meson

%files -f %{_sourcedir}/meson.filelist

%changelog
* Wed Nov 11 2026 tenko <build@tenko.invalid> 1.12.1-4
- Rebuild with tenko-rpm-config 6-4 for the generated python(abi) = 3.15 requirement on its Python modules.

* Sat Nov 07 2026 tenko <build@tenko.invalid> 1.12.1-3
- Install the upstream bash and zsh completions from data/shell-completions;
  setup.py installs the Python package but not the shell completion files.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.12.1-2
- Record the verified license (Apache-2.0): COPYING (issue #8).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 1.12.1-1
- Update to 1.12.1 (current upstream version).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.12.0
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.1
- Version bump
