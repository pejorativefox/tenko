Name:       libnotify
Version:    0.8.9
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    libnotify-0.8.9.tar.xz

%description
TODO

%package devel
Summary:    libnotify development files
Requires:   %{name}-gir = %{version}-%{release}
Requires:   libnotify = %{version}-%{release}

%description devel
Development files for libnotify.

%prep
%setup -a 0

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release -D gtk_doc=false -D man=false -D tests=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd


%package gir
Summary:    GObject Introspection data for libnotify
License:    GPL3
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for libnotify, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the -devel package.

%files -f %{_sourcedir}/libnotify.filelist
%files devel -f %{_sourcedir}/libnotify-devel.filelist
%files gir -f %{_sourcedir}/libnotify-gir.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.8.9-1
- Update to 0.8.9 (BLFS r13.1 trunk, D9 parity)
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.8.8-2
- Split devel payload into libnotify-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.8.8
- Sync with BLFS r13.1 (0.7.8)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.7.8-1
- Version bump

