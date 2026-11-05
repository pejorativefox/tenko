Name:       dtc
Version:    1.8.1
Release:    3
Summary:    Device Tree Compiler and libfdt
License:    GPL-2.0-or-later AND BSD-2-Clause
URL:        https://www.devicetree.org/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
The Device Tree Compiler (dtc) translates device tree source into the
binary blob (DTB) format used by the Linux kernel, and provides the
utilities fdtget, fdtput and fdtdump.  The package also ships libfdt, a
library for reading and manipulating flat device trees at runtime.

dtc-1.8.1 is the version in BLFS r13.1 (general/prog/dtc).

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release --default-library=shared \
      -Dpython=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/dtc.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.8.1-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.8.1-1
- New package for the qemu dependency chain.  dtc is in BLFS r13.1 at
  1.8.1.
- Source: https://kernel.org/pub/software/utils/dtc/dtc-1.8.1.tar.xz
  md5 9753bdbf18763efef1f5ae8c0cecb5f6
- Built with meson (shared libfdt, python bindings disabled) exactly as
  the book does; qemu uses libfdt for system device trees.
