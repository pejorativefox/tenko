Name:       libnvme
Version:    1.16.2
Release:    1
Summary:    NVMe management library
License:    LGPL-2.1-or-later AND GPL-2.0-or-later
URL:        https://github.com/linux-nvme/libnvme
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

%description
libnvme is a library for discovering, configuring and managing NVMe
controllers and namespaces.  It provides the ioctl wrappers, the sysfs
topology parser and the MI/MCTP transport used by libblockdev's nvme plugin
and other NVMe tools.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. \
    --prefix=/usr \
    --libdir=%{_libdir} \
    --buildtype=release \
    -Ddefault_library=shared \
    -Ddocs=false \
    -Ddocs-build=false \
    -Dexamples=false \
    -Dtests=false \
    -Dpython=disabled \
    -Dlibdbus=disabled \
    -Dliburing=disabled \
    -Dopenssl=enabled \
    -Djson-c=enabled \
    -Dkeyutils=enabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libnvme.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 1.16.2-1
- Initial package at the latest stable upstream release, 1.16.2.
- Verified the licence as LGPL-2.1-or-later AND GPL-2.0-or-later from
  COPYING and the per-file SPDX headers (most files LGPL-2.1-or-later,
  src/nvme/base64.c GPL-2.0-or-later).
- Built the shared libraries only, without docs, examples, tests, Python
  bindings, libdbus, liburing or MCTP dbus support.
