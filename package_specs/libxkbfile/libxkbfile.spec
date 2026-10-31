Name:       libxkbfile
Version:    1.2.0
Release:    1
Summary:    library to parse the XKB configuration data files
License:    GPL3
Prefix:     /usr
Source0:    libxkbfile-1.2.0.tar.xz

%description
libxkbfile is used by the X servers and utilities to parse the XKB configuration data files

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libxkbfile.filelist

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.2.0
- Sync with BLFS r13.1 (1.1.2)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.2-1
- Version bump
