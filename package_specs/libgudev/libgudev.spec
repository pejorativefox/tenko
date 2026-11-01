Name:       libgudev
Version:    238
Release:    2
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    libgudev-238.tar.xz

%description
TODO

%package devel
Summary:    libgudev development files
Requires:   libgudev = %{version}-%{release}

%description devel
Development files for libgudev.

%prep
%setup -a 0

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

%files -f %{_sourcedir}/libgudev.filelist
%files devel -f %{_sourcedir}/libgudev-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 238-2
- Split devel payload into libgudev-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 238
- Sync with BLFS r13.1 (230)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 230-1
- Version bump
