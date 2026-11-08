# libtsm is the DEC VT100-VT520 terminal state machine used by kmscon.  It
# does no rendering and has no graphics-stack dependency.  The build keeps the
# headers, unversioned .so link and pkg-config file in the runtime package:
# Tenko has no -devel subpackages.
Name:       libtsm
Version:    4.8.0
Release:    1
Summary:    DEC-VT terminal emulator state machine
License:    MIT AND LGPL-2.1-or-later
URL:        https://github.com/kmscon/libtsm
Prefix:     /usr
Source0:    libtsm-%{version}.tar.gz

BuildRequires: meson
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: libxkbcommon

%description
libtsm is a state machine for DEC VT100-VT520 compatible terminal emulators.
It can be used to implement terminal emulators or other applications that
need to interpret terminal escape sequences.  The library does no rendering
or window management of its own and does not depend on a graphics stack.

This is the kmscon project's current libtsm 4.8.0 release, used by the kmscon
package.  The library is MIT licensed; the bundled hash-table helper carries
LGPL-2.1-or-later (LICENSE_htable).

%prep
%setup -q

%build
mkdir -p build
pushd build
meson setup .. --prefix=%{_prefix} --buildtype=release \
    -Dtests=false -Dgtktsm=false
ninja
popd

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} ninja -C build install
install -d -m 0755 %{buildroot}%{_datadir}/doc/libtsm
install -m 0644 COPYING %{buildroot}%{_datadir}/doc/libtsm/COPYING
install -m 0644 LICENSE_htable %{buildroot}%{_datadir}/doc/libtsm/LICENSE_htable
install -m 0644 README.md %{buildroot}%{_datadir}/doc/libtsm/README.md

%files -f %{_sourcedir}/libtsm.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.8.0
- Package libtsm 4.8.0 (latest stable release) as the terminal state
  machine kmscon links against.  Headers, the unversioned .so link and the
  pkg-config file stay in the runtime package per the no-devel policy.
