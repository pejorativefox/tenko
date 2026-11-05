Name:       gtkmm
Version:    3.24.11
Release:    1
Summary:    gtkmm is the official C++ interface for the popular GUI library GTK+.
License:    LGPL
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

BuildRequires: cairomm
BuildRequires: pangomm
BuildRequires: atkmm
BuildRequires: glibmm

%description
gtkmm is the official C++ interface for the popular GUI library GTK+.

%prep
%setup -q

%build
mkdir gtk-build
pushd gtk-build
meson setup --prefix=/usr --buildtype=release ..
ninja
popd

%install
rm -rf %{buildroot}
pushd gtk-build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/gtkmm.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 3.24.11-1
- Sync with BLFS r13.1 (gtkmm3.xml)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 3.24.8-1
- Version bump

* Sun May 17 2020 Chris Statzer <chris.statzer@qq.com> 3.24.2-1
- Initial RPM
