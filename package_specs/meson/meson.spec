Name:       meson
Version:    1.12.0
Release:    1
Summary:    Meson build system
License:    GPL3
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
/usr/lib64/python3.14/site-packages/
/usr/share/man/man1/meson.1.gz
/usr/share/polkit-1/actions/com.mesonbuild.install.policy

%changelog
* Fri Oct 30 2026 browneye <build@browneye.invalid> 1.12.0
- Sync with LFS r13.1

* Mon Sep 4 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.1
- Version bump
