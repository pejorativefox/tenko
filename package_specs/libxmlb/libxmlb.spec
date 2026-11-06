Name:       libxmlb
Version:    0.3.29
Release:    4
Summary:    Library for querying compressed XML metadata
License:    LGPL-2.1-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
libxmlb provides a compressed XML metadata store with fast XPath-like
queries.  AppStream requires it for its metadata cache.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -Dgtkdoc=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libxmlb.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.3.29-4
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later): LICENSE and the SPDX headers in src/*.c (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.3.29-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.3.29-1
- New package, synced with the base set.  Required by AppStream.
