Name:       libxml2
Version:    2.15.3
Release:    1
Summary:    XML parsing library
License:    GPL3
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
* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.15.3
- Sync with BLFS r13.1 (2.10.4)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2.10.4
- Version bump
