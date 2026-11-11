Name:       fwupd
Version:    2.1.9
Release:    1
Summary:    Firmware update daemon and command-line tools
License:    LGPL-2.1-or-later
URL:        https://fwupd.org/
Source0:    %{name}-%{version}.tar.xz
BuildRequires: gcc
BuildRequires: meson
BuildRequires: ninja
BuildRequires: gettext
BuildRequires: glib
BuildRequires: libxmlb >= 0.3.19
BuildRequires: libusb >= 1.0.27
BuildRequires: curl >= 7.62
BuildRequires: sqlite
BuildRequires: systemd >= 249
BuildRequires: polkit >= 0.103
BuildRequires: gnutls >= 3.6
BuildRequires: libdrm
BuildRequires: util-linux
BuildRequires: zlib
BuildRequires: xz
BuildRequires: readline
BuildRequires: bash-completion
BuildRequires: hwdata
BuildRequires: python
BuildRequires: python-jinja
Requires:   fwupd-efi >= 1.9
Requires:   hwdata
Requires:   glib
Requires:   libxmlb >= 0.3.19
Requires:   libusb >= 1.0.27
Requires:   curl
Requires:   sqlite
Requires:   systemd >= 249
Requires:   polkit >= 0.103
Requires:   gnutls
Requires:   libdrm
Requires:   util-linux
Requires:   zlib
Requires:   xz
Requires:   readline
Prefix:     /usr
BuildRequires: openssl
BuildRequires: shadow
BuildRequires: python-markupsafe

%description
fwupd is a system daemon and set of command-line tools for updating firmware
on Linux.  It discovers updatable devices through plugins, downloads metadata
from the LVFS, and applies firmware updates, including UEFI capsule and
vendor-specific device updates.  This build ships the D-Bus system service,
polkit policy, fwupdmgr and fwupdtool, and the UEFI capsule plugin backed by
fwupd-efi.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                              \
      --prefix=/usr                         \
      --buildtype=release                   \
      -Dsupported_build=enabled             \
      -Ddocs=disabled                       \
      -Dintrospection=disabled              \
      -Dman=true                            \
      -Dmetainfo=true                       \
      -Dtests=false                         \
      -Dumockdev_tests=disabled             \
      -Dvalgrind=disabled                   \
      -Dudev_hotplug=true                   \
      -Dbluez=disabled                      \
      -Dlibdrm=enabled                      \
      -Dlibmnl=disabled                     \
      -Dpassim=disabled                     \
      -Dhsi=enabled                         \
      -Dpolkit=enabled                      \
      -Dgnutls=enabled                      \
      -Dopenssl=disabled                    \
      -Dsystemd=enabled                     \
      -Dlogind=enabled                      \
      -Dplugin_modem_manager=disabled       \
      -Dplugin_uefi_capsule_splash=false    \
      -Defi_binary=false                    \
      -Dbash_completion=true                \
      -Dfish_completion=true                \
      -Dvendor_ids_dir=/usr/share/hwdata
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
install -Dpm0644 COPYING %{buildroot}/usr/share/licenses/fwupd/COPYING
install -d -m0755 %{buildroot}/var/lib/fwupd %{buildroot}/var/cache/fwupd

%post
# The Tenko systemd package does not ship a sysusers.d file trigger, so
# create the fwupd-refresh account immediately (same pattern as flatpak).
if [ -x /usr/bin/systemd-sysusers ]; then
    /usr/bin/systemd-sysusers /usr/lib/sysusers.d/fwupd.conf || :
fi
if [ -x /usr/bin/systemctl ]; then
    /usr/bin/systemctl --root=/ enable fwupd-refresh.timer >/dev/null 2>&1 || :
fi

%files -f %{_sourcedir}/fwupd.filelist

%changelog
* Mon Nov 09 2026 browneye <build@browneye.invalid> 2.1.9-1
- Initial package: latest stable upstream release 2.1.9.  fwupd 2.x folds
  its former libjcat/gcab helpers into libfwupd/libfwupdplugin and uses
  libusb directly instead of libgusb, so no separate gusb, libjcat or gcab
  packages are required.
- Plugins are enabled only where their build dependencies exist.  Passim,
  libmnl (devlink), ModemManager and BlueZ support are disabled explicitly;
  the UEFI capsule splash is disabled because python-cairo/Pango are not
  packaged, but UEFI capsule updates themselves remain enabled through
  fwupd-efi.
- Licence verified from COPYING and the per-file SPDX headers
  (LGPL-2.1-or-later).
