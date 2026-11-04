Name:       libxmlb
Version:    0.3.29
Release:    1
Summary:    Library for querying compressed XML metadata
License:    LGPL
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
* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.3.29-1
- New package, synced with BLFS r13.1.  Required by AppStream.
