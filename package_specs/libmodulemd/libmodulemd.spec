Name:       libmodulemd
Version:    2.15.3
Release:    1
Summary:    C library for manipulating module metadata files
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
libmodulemd is a C library for manipulating the module metadata (modulemd)
files used by dnf and libdnf.

%prep
%setup -q -n %{name}-libmodulemd-%{version}

%build
mkdir build
pushd build
meson setup ..                 \
      --prefix=/usr            \
      --buildtype=release      \
      -Dwith_docs=false        \
      -Dwith_manpages=disabled \
      -Dskip_introspection=true \
      -Dwith_py3=false         \
      -Drpmio=enabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libmodulemd.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.15.3-1
- Update to 2.15.3 (was 2.15.0 in the modulemd spec) for the E1 dnf/libdnf
  chain; renamed the spec directory/package from modulemd to libmodulemd to
  match upstream and BLFS-style naming.
- libmodulemd is not in LFS/BLFS; current libdnf and createrepo_c require
  modulemd-2.0 >= 2.9.3.
- GObject Introspection and Python 3 bindings are disabled; only libdnf's
  C API is needed.
- Use a generated static filelist.
