Name:       libxml2
Version:    2.15.4
Release:    4
Summary:    XML parsing library
License:    MIT
URL:        https://gitlab.gnome.org/GNOME/libxml2
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
%description
The libxml2 package contains libraries and utilities used for parsing XML files. 

%prep
%setup -q
sed -i "/'git'/,+3d" meson.build

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -D history=enabled  \
      -D icu=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxml2.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.15.4-4
- Record the verified license (MIT): Copyright (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.15.4-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.15.4-2
- Split devel payload into libxml2-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.15.3
- Sync with 2.10.4

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2.10.4
- Version bump
