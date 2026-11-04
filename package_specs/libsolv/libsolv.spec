Name:       libsolv
Version:    0.7.41
Release:    5
Summary:    Library for solving packages and reading repositories
License:    BSD
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
libsolv is a dependency solver and repository reader used by libdnf and
dnf.  This build includes the RPM database (via librpm), rpmmd and RPM
package readers required by libdnf.

%package devel
Summary:    Development files for libsolv
Requires:   %{name} = %{version}-%{release}

%description devel
pkg-config files for libsolv, used to build software against it.

%prep
%setup -q

%build
mkdir build
pushd build
cmake -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_INSTALL_LIBDIR=lib64    \
      -DCMAKE_BUILD_TYPE=Release     \
      -DENABLE_COMPLEX_DEPS=ON       \
      -DENABLE_RPMDB=ON              \
      -DENABLE_RPMDB_LIBRPM=ON       \
      -DENABLE_RPMPKG=ON             \
      -DENABLE_RPMPKG_LIBRPM=ON      \
      -DENABLE_RPMMD=ON              \
      -DENABLE_LZMA_COMPRESSION=ON   \
      -DENABLE_BZIP2_COMPRESSION=ON  \
      -DENABLE_ZSTD_COMPRESSION=ON   \
      -DENABLE_ZCHUNK_COMPRESSION=ON \
      -DWITH_SYSTEM_ZCHUNK=ON        \
      -DENABLE_PYTHON=OFF            \
      -DENABLE_PERL=OFF              \
      -DENABLE_RUBY=OFF              \
      -DENABLE_TCL=OFF               \
      -DENABLE_LUA=OFF               \
      ..
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} cmake --install .
popd
# FindLibSolv.cmake is installed under /usr/share/cmake/Modules, but CMake
# searches ${CMAKE_ROOT}/Modules (here /usr/share/cmake-4.4/Modules) and
# CMAKE_MODULE_PATH, not the generic /usr/share/cmake/Modules.  Install a
# copy in the real module directory so find_package(LibSolv) works.
cmake_root=$(cmake --system-information 2>/dev/null | sed -n 's/^CMAKE_ROOT "\([^"]*\)"/\1/p' | head -1)
[ -n "$cmake_root" ] || cmake_root=/usr/share/cmake
install -Dm0644 cmake/modules/FindLibSolv.cmake \
    "%{buildroot}${cmake_root}/Modules/FindLibSolv.cmake"

%files -f %{_sourcedir}/libsolv.filelist
%files devel -f %{_sourcedir}/libsolv-devel.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.7.41-5
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.7.41-3
- Move the pkg-config files into a new -devel subpackage so the runtime
  package no longer drags pkgconfig(...) consumers into every install.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.7.41-2
- Rebuild for Python 3.15 / the D9 dnf stack refresh (new NEVR so the
  rebuilt package supersedes the published -1).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.7.41-1
- Update to upstream 0.7.41 (was 0.7.24) for the E1 dnf/libdnf chain.
  libsolv is not in LFS/BLFS; current libdnf requires >= 0.7.21.
- Enable the RPM database/rpmmd/rpmpkg readers (librpm based) that
  libdnf uses, plus lzma/bzip2/zstd/zchunk compression.
- Do not build the perl/python/ruby/tcl/lua language bindings.
- Use a generated static filelist.
