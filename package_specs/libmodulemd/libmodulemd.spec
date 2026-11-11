Name:       libmodulemd
Version:    2.15.3
Release:    6
Summary:    C library for manipulating module metadata files
License:    MIT
URL:        https://github.com/fedora-modularity/libmodulemd
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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.15.3-6
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 2.15.3-5
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.15.3-3
- Move the pkg-config files into a new -devel subpackage so the runtime
  package no longer drags pkgconfig(...) consumers into every install.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 2.15.3-2
- Rebuild for Python 3.15 / the D9 dnf stack refresh (new NEVR so the
  rebuilt package supersedes the published -1).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.15.3-1
- Update to 2.15.3 (was 2.15.0 in the modulemd spec) for the E1 dnf/libdnf
  chain; renamed the spec directory/package from modulemd to libmodulemd to
  match upstream naming.
- libmodulemd is not in the base set; current libdnf and createrepo_c require
  modulemd-2.0 >= 2.9.3.
- GObject Introspection and Python 3 bindings are disabled; only libdnf's
  C API is needed.
- Use a generated static filelist.
