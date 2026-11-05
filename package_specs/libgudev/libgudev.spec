Name:       libgudev
Version:    238
Release:    5
Summary:    GObject bindings for libudev
License:    LGPL-2.1-or-later
Prefix:     /usr
Source0:    libgudev-238.tar.xz

%description
libgudev is a library providing GObject bindings for libudev. It used to
be part of udev and then systemd, and is now a project on its own.

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
License:    LGPL-2.1-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for libgudev, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/libgudev.filelist
%files gir -f %{_sourcedir}/libgudev-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 238-5
- Replace the TODO summary/description and record the verified license
  (LGPL-2.1-or-later): meson.build (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 238-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 238-3
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 238-2
- Split devel payload into libgudev-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 238
- Sync with BLFS r13.1 (230)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 230-1
- Version bump
