Name:       librepo
Version:    1.21.3
Release:    2
Summary:    Library for downloading and reading RPM repository metadata
License:    LGPL
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
librepo is a library providing a C and Python API for downloading and
reading RPM repository metadata.  It is a core dependency of libdnf.

%prep
%setup -q

%build
mkdir build
pushd build
cmake -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_INSTALL_LIBDIR=lib64 \
      -DCMAKE_BUILD_TYPE=Release  \
      -DENABLE_TESTS=OFF          \
      -DENABLE_DOCS=OFF           \
      -DENABLE_EXAMPLES=OFF       \
      -DENABLE_PYTHON=OFF         \
      -DENABLE_SELINUX=OFF        \
      -DUSE_GPGME=ON              \
      -DWITH_ZCHUNK=ON            \
      ..
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} cmake --install .
popd

%files -f %{_sourcedir}/librepo.filelist

%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.21.3-2
- Rebuild for Python 3.15 / the D9 dnf stack refresh (new NEVR so the
  rebuilt package supersedes the published -1).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.21.3-1
- Update to 1.21.3 (was 1.15.2) for the E1 dnf/libdnf chain.  librepo is
  not in LFS/BLFS; current libdnf requires >= 1.18.0.
- Built with gpgme and zchunk support; SELinux support is disabled (the
  distro has no libselinux) and the optional Python bindings are not
  needed by dnf.
- Use a generated static filelist.
