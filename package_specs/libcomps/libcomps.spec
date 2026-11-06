Name:       libcomps
Version:    0.1.24
Release:    7
Summary:    Comps XML file manipulation library
License:    GPL-2.0-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
libcomps is a library for structure-like manipulation of the content of
comps XML files.  It supports reading and writing XML, modifying structures
and the Python bindings used by dnf.

%prep
%setup -q

%build
mkdir build
pushd build
cmake -S ../libcomps -B .          \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_INSTALL_LIBDIR=lib64 \
      -DCMAKE_BUILD_TYPE=Release  \
      -DENABLE_TESTS=OFF          \
      -DENABLE_DOCS=OFF
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} cmake --install .
popd

%files -f %{_sourcedir}/libcomps.filelist
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.1.24-7
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later): COPYING, plus libcomps/src/*.c "either version 2 ... or any later version" (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.1.24-6
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.1.24-5
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.1.24-3
- Move the pkg-config files into a new -devel subpackage so the runtime
  package no longer drags pkgconfig(...) consumers into every install.

* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.1.24-2
- Rebuild for Python 3.15 (3.14 site-packages are gone); 0 paths updated.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.1.24-1
- New package (replaces the stale 0.1.15 python-libcomps spec) for the E1
  dnf/libdnf chain.
- Builds the C library, headers and the libcomps Python module from the
  same source tree; libcomps is not in the base set and current libdnf requires
  >= 0.1.8.
- Use a generated static filelist.
