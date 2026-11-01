Name:       libxkbfile
Version:    1.2.0
Release:    2
Summary:    library to parse the XKB configuration data files
License:    GPL3
Prefix:     /usr
Source0:    libxkbfile-1.2.0.tar.xz

%description
libxkbfile is used by the X servers and utilities to parse the XKB configuration data files

%package devel
Summary:    libxkbfile development files
Requires:   libxkbfile = %{version}-%{release}

%description devel
Development files for libxkbfile.

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
%files devel -f %{_sourcedir}/libxkbfile-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.0-2
- Split devel payload into libxkbfile-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.2.0
- Sync with BLFS r13.1 (1.1.2)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.2-1
- Version bump
