Name:       libxkbcommon
Version:    1.13.2
Release:    4
Summary:    library for handling of keyboard descriptions
License:    MIT AND MIT-open-group AND HPND AND HPND-sell-variant AND ISC AND LicenseRef-digital-equipment-corporation
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
%description
library for handling of keyboard descriptions

%prep
%setup -q
patch -Np1 -i %{_sourcedir}/libxkbcommon-1.13.2-upstream_fix-1.patch

%build
mkdir build &&
cd    build &&

meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -Denable-wayland=false \
      -Denable-docs=false 
ninja

%install    
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxkbcommon.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.13.2-4
- Record the verified license (MIT AND MIT-open-group AND HPND AND HPND-sell-variant AND ISC AND LicenseRef-digital-equipment-corporation): LICENSE (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.13.2-3
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.13.2-2
- Split devel payload into libxkbcommon-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.13.2
- Sync with BLFS r13.1 (1.5.0)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.0-1
- Version bump

