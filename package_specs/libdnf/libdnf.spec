Name:       libdnf
Version:    0.76.0
Release:    2
Summary:    Library providing a simplified C and Python API to libsolv
License:    LGPL
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
libdnf is the library that provides the package-management engine used by
dnf: repository handling, dependency solving through libsolv, RPM
transactions and the hawkey Python bindings.

%prep
%setup -q

%build
mkdir build
pushd build
cmake -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_INSTALL_LIBDIR=lib64 \
      -DCMAKE_BUILD_TYPE=Release  \
      -DWITH_BINDINGS=ON          \
      -DWITH_GTKDOC=OFF           \
      -DWITH_HTML=OFF             \
      -DWITH_MAN=OFF              \
      -DWITH_TESTS=OFF            \
      -DWITH_ZCHUNK=ON            \
      -DENABLE_RHSM_SUPPORT=OFF   \
      ..
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} cmake --install .
popd

%files -f %{_sourcedir}/libdnf.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.76.0-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 0 paths updated.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.76.0-1
- Update to 0.76.0 (was 0.71.0) for the E1 dnf/libdnf chain.  libdnf is
  not in LFS/BLFS; this is the current release of the dnf-4 branch, which
  is the branch that supports the rpm 4.18.1 in the base image (dnf5 needs
  rpm >= 4.19).
- Python/SWIG bindings are enabled (dnf 4 is Python based); gtk-doc, HTML
  and man pages, unit tests and RHSM support are disabled.
- Use a generated static filelist.
