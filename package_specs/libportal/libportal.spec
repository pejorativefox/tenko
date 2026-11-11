Name:       libportal 
Version:    0.9.1
Release:    2
Summary:    Flatpak portal library 
License:    LGPL-3.0-only
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Flatpak portal library 

%prep
%setup

%build
mkdir build
pushd build
meson setup ..                 \
      --prefix=/usr            \
      --buildtype=release      \
      -D backend-gtk4=disabled \
      -D backend-qt5=disabled  \
      -D backend-qt6=disabled  \
      -D docs=false            \
      -D vapi=false            \
      -D tests=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libportal.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.9.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-3.0-only): COPYING, LGPL v3, and the SPDX headers in libportal/*.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.9.1-1
- Sync with the base set

* Tue Jan 19 2021 Chris Statzer <chris.statzer@qq.com> 0.3
- Initial RPM

