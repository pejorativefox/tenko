Name:       awesome
Version:    4.3
Release:    1
Summary:    Highly configurable X11 window manager
License:    GPL3
Prefix:     /usr
URL:        https://awesomewm.org/
Source0:    %{name}-%{version}.tar.xz
Patch0:     %{name}-%{version}-cmake-check-examples.patch

%description
awesome is a highly configurable, next generation framework window
manager for X11.  It is extended using the Lua programming language.

%prep
%setup -q
%patch -P 0 -p1

%build
mkdir build
pushd build
cmake ..                              \
      -DCMAKE_INSTALL_PREFIX:PATH=/usr \
      -DCMAKE_BUILD_TYPE=Release      \
      -DCMAKE_C_FLAGS=-fcommon        \
      -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
      -DLUA_INCLUDE_DIR=/usr/include  \
      -DLUA_LIBRARY=/usr/lib64/liblua.so \
      -DGENERATE_DOC=OFF              \
      -DGENERATE_MANPAGES=OFF         \
      -DWITH_DBUS=ON
%make_build
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} %make_install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/awesome.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.3-1
- Update to 4.3; not in the r13.1 book, latest upstream stable
  2026-11-05 (4.3 is the latest tagged release).
- Build with the book's Lua 5.4 and the upstream Lua 5.4 lgi build
  fix; the Lua 5.3 paths and bz2 source of the old spec are gone.
- Disable API documentation and man pages; DBus support stays on.
- CMAKE_POLICY_VERSION_MINIMUM=3.5 is needed because awesome 4.3
  declares cmake_minimum_required(VERSION 3.0.0), which CMake 4
  rejects.
- Build with -fcommon: awesome 4.3 generates headers that define
  key_class, global_signals and lualib_dofunction_on_error in every
  translation unit, which GCC 10 and later reject with -fno-common.
- Build from the upstream release asset; the extracted top directory
  is awesome-4.3.
