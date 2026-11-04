Name:       libxmlb
Version:    0.3.29
Release:    3
Summary:    Library for querying compressed XML metadata
License:    LGPL
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
libxmlb provides a compressed XML metadata store with fast XPath-like
queries.  AppStream requires it for its metadata cache.

%package devel
Summary:    Development files for libxmlb
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in libxmlb; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

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
%files devel

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.3.29-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.3.29-1
- New package, synced with BLFS r13.1.  Required by AppStream.
