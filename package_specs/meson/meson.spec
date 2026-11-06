Name:       meson
Version:    1.12.1
Release:    2
Summary:    Meson build system
License:    Apache-2.0
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

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

%files
/usr/bin/meson
/usr/lib64/python3.15/site-packages/
/usr/share/man/man1/meson.1.gz
/usr/share/polkit-1/actions/com.mesonbuild.install.policy

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.12.1-2
- Record the verified license (Apache-2.0): COPYING (issue #8).

* Mon Nov  2 2026 browneye <build@browneye.invalid> 1.12.1-1
- Update to 1.12.1 (current upstream version).

* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.12.0
- Sync with the base set

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.1
- Version bump
