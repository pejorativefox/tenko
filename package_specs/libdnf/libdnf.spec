Name:       libdnf
Version:    0.76.0
Release:    8
Summary:    Library providing a simplified C and Python API to libsolv
License:    LGPL-2.1-or-later AND LGPL-3.0-or-later
URL:        https://github.com/rpm-software-management/libdnf
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz
BuildRequires: openssl
BuildRequires: swig

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
* Wed Nov 11 2026 tenko <build@tenko.invalid> 0.76.0-8
- Rebuild with tenko-rpm-config 6-4 for the generated python(abi) = 3.15 requirement on its Python modules.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.76.0-7
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later AND LGPL-3.0-or-later): COPYING, plus libdnf/utils/bgettext/bgettext.c, which is LGPLv3+ (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.76.0-6
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.76.0-5
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.76.0-3
- Move the pkg-config files into a new -devel subpackage so the runtime
  package no longer drags pkgconfig(...) consumers into every install.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.76.0-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 0 paths updated.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.76.0-1
- Update to 0.76.0 (was 0.71.0) for the E1 dnf/libdnf chain.  libdnf is
  not in the base set; this is the current release of the dnf-4 branch, which
  is the branch that supports the rpm 4.18.1 in the base image (dnf5 needs
  rpm >= 4.19).
- Python/SWIG bindings are enabled (dnf 4 is Python based); gtk-doc, HTML
  and man pages, unit tests and RHSM support are disabled.
- Use a generated static filelist.
