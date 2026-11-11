Name:       bluez
Version:    5.88
Release:    1
Summary:    Bluetooth protocol stack for Linux
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
URL:        https://github.com/bluez/bluez
Prefix:     /usr
Source0:    bluez-%{version}.tar.xz
BuildRequires: glib
BuildRequires: dbus-libs
BuildRequires: systemd
BuildRequires: readline
BuildRequires: python3-docutils
BuildRequires: dbus-daemon
Requires:   dbus-daemon
Requires:   systemd

%description
BlueZ is the official Linux Bluetooth protocol stack.  It provides the
bluetoothd daemon (D-Bus API org.bluez), the bluetoothctl command line
client, btmon, the HCI and audio helper tools, libbluetooth and the
bluetooth.target integration.

%prep
%setup -q

%build
%configure                       \
    --prefix=/usr                \
    --libdir=/usr/lib64          \
    --sysconfdir=/etc            \
    --localstatedir=/var         \
    --libexecdir=/usr/libexec    \
    --with-dbusconfdir=/etc      \
    --enable-library             \
    --enable-tools               \
    --enable-client              \
    --enable-monitor             \
    --enable-systemd             \
    --enable-udev                \
    --enable-datafiles           \
    --enable-manpages            \
    --enable-hid2hci             \
    --disable-sixaxis            \
    --disable-obex               \
    --disable-cups               \
    --disable-mesh               \
    --disable-midi               \
    --disable-testing            \
    --disable-deprecated         \
    --disable-experimental       \
    --with-zsh-completion-dir=no
%make_build

%install
rm -rf %{buildroot}
%make_install
# bluez creates per-adapter state under this directory; the daemon runs as
# root and the adapters' keys must not be world readable.
install -dm700 %{buildroot}/var/lib/bluetooth
mkdir -p %{buildroot}/usr/lib/systemd/system-preset
install -m644 %{_sourcedir}/40-tenko-bluetooth.preset \
    %{buildroot}/usr/lib/systemd/system-preset/40-tenko-bluetooth.preset

%post
# Apply the shipped preset so upgrades of existing installs, which never run
# preset-all again, enable the daemon as well.
if [ -x /usr/bin/systemctl ]; then
    systemctl preset bluetooth.service >/dev/null 2>&1 || :
fi

%files -f %{_sourcedir}/bluez.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 5.88-1
- New package: BlueZ 5.88 (latest stable upstream, released 2026-11-05).
  The daemon, bluetoothctl, btmon, the HCI helpers, libbluetooth and the
  D-Bus/systemd/udev integration are enabled; obex (no libical yet), CUPS,
  mesh (no ell) and the deprecated hcitool set are disabled.
