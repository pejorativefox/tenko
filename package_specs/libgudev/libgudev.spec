Name:       libgudev
Version:    238
Release:    3
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    libgudev-238.tar.xz

%description
TODO

%package devel
Summary:    libgudev development files
Requires:   %{name}-gir = %{version}-%{release}
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


%package gir
Summary:    GObject Introspection data for libgudev
License:    GPL3
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for libgudev, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the -devel package.

%files -f %{_sourcedir}/libgudev.filelist
%files devel -f %{_sourcedir}/libgudev-devel.filelist
%files gir -f %{_sourcedir}/libgudev-gir.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 238-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 238-2
- Split devel payload into libgudev-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 238
- Sync with BLFS r13.1 (230)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 230-1
- Version bump
