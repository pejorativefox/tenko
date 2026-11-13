Name:       nvme-cli
Version:    3.2
Release:    1
Summary:    NVMe management command line interface
License:    GPL-2.0-only AND LGPL-2.1-or-later
URL:        https://github.com/linux-nvme/nvme-cli
Source0:    %{name}-%{version}.tar.gz
Prefix:     /usr

Requires:   systemd

BuildRequires: gcc
BuildRequires: meson
BuildRequires: ninja
BuildRequires: json-c
BuildRequires: kmod
BuildRequires: keyutils
BuildRequires: openssl
BuildRequires: libarchive
BuildRequires: systemd

%description
nvme-cli is the userspace tool for NVMe storage.  It lists controllers and
namespaces, reads identify, SMART/health and error logs, runs self-tests,
formats namespaces, manages firmware, and configures NVMe over Fabrics
connections.

The 3.x source tree bundles libnvme3.  This package installs the nvme
command, the nvme-discoverd daemon and the libnvme3 shared library with its
headers and pkg-config file; Tenko has no -devel subpackages.  The separate
libnvme 1.16.2 package stays in place for libblockdev's nvme plugin.

nvme-cli is not part of the base set; it is an optional storage diagnostic
and management tool.  The daemons are installed but not enabled by default.

%prep
%setup -q -n %{name}-%{version}

%build
mkdir build
pushd build
meson setup \
    --prefix=/usr \
    --libdir=%{_libdir} \
    --sysconfdir=/etc \
    --buildtype=release \
    -Ddocs=man \
    -Dtests=false \
    -Dexamples=false \
    -Dpython=disabled \
    -Dnvme-discoverd=enabled \
    -Dnvme-keysd=disabled \
    -Dprivsep=disabled \
    -Dsandbox=disabled \
    -Dliburing=disabled \
    -Dlibdbus=disabled \
    ..
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%post
if [ -x /usr/bin/systemctl ]; then
    systemctl daemon-reload >/dev/null 2>&1 || :
fi

%postun
if [ -x /usr/bin/systemctl ]; then
    systemctl daemon-reload >/dev/null 2>&1 || :
fi

%files -f %{_sourcedir}/nvme-cli.filelist

%changelog
* Fri Nov 13 2026 tenko <build@tenko.invalid> 3.2-1
- New package: nvme-cli 3.2 (latest stable upstream, released 2026-10-30,
  checked 2026-11-13).  Not in the base set.
- The 3.x source tree bundles libnvme3; the package installs
  libnvme3.so.1, its headers and libnvme3.pc.  The separate libnvme 1.16.2
  package remains for libblockdev's nvme plugin.
- Man pages come from the committed pages (-Ddocs=man).  Tests, examples,
  Python bindings and the privsep, sandbox and keysd technology previews
  are disabled; nvme-discoverd is built.
