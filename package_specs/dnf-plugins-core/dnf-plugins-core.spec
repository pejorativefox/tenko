Name:       dnf-plugins-core
Version:    4.4.2
Release:    1
Summary:    Core DNF Plugins 
License:    GPL
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

BuildRequires: dnf

%description
Core DNF pluigins providing additional dnf functionality.

%prep
%setup

%build
mkdir build
pushd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr \
         -DPYTHON_DESIRED=3
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
%make_install
popd
rm %{buildroot}/etc/dnf/plugins/local.conf

%files
/etc/dnf/plugins
/usr/lib/python3.7/site-packages/dnfpluginscore/__init__.py
/usr/lib/python3.7/site-packages/dnf-plugins/
/usr/libexec/dnf-utils-3
/usr/share/locale/
/usr/share/man/

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.4.2-1
- Build without the Sphinx documentation stack, which was retired from
  the distro; the man pages are no longer generated.

* Sun May 24 2020 Chris Statzer <chris.statzer@qq.com> 4.0.15-1
- Initial RPM

