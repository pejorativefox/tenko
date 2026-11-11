Name:       json-c
Version:    0.19
Release:    3
Summary:    JSON implementation in C
License:    MIT
URL:        https://github.com/json-c/json-c
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
JSON-C implements a reference counting object model that allows you to
easily construct JSON objects in C, output them as JSON formatted strings
and parse JSON formatted strings back into the C representation of JSON
objects.

%prep
%setup -q

%build
mkdir build
pushd build
cmake -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_INSTALL_LIBDIR=lib64   \
      -DCMAKE_BUILD_TYPE=Release    \
      -DBUILD_SHARED_LIBS=ON        \
      -DBUILD_STATIC_LIBS=OFF       \
      -DCMAKE_INSTALL_DOCDIR=/usr/share/doc/%{name}-%{version} \
      ..
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} cmake --install .
popd

%files -f %{_sourcedir}/json-c.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.19-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.19-1
- New package for the self-hosted dnf/libdnf toolchain (E1).
- Pinned version (json-c 0.19).  Built with shared libraries only.
