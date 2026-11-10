Name:       tuned
Version:    2.28.0
Release:    1
Summary:    Dynamic adaptive system tuning daemon
License:    GPL-2.0-or-later AND CC-BY-SA-3.0
URL:        https://tuned-project.org/
Source0:    %{name}-%{version}.tar.gz
Source1:    tuned.preset
Prefix:     /usr
BuildArch:  noarch
BuildRequires: desktop-file-utils
BuildRequires: make
BuildRequires: python
Requires:   python3-dbus
Requires:   python3-gobject
Requires:   python3-linux-procfs
Requires:   python3-pyudev
Requires:   virt-what
Requires:   ethtool
Requires:   iw
Requires:   hdparm
Requires:   dmidecode
Requires:   gawk
Requires:   util-linux
Requires:   dbus-daemon
Requires:   dbus-libs
Requires:   polkit
Requires:   systemd
Requires:   kmod
Requires:   iproute2

%description
TuneD is a daemon that tunes system settings dynamically.  It monitors the
use of system components periodically and adjusts settings to improve
performance, latency, power consumption or thermal behaviour for the active
profile.  The package ships tuned-adm, the built-in profiles and the systemd,
D-Bus and polkit integration.

This build ships the daemon, tuned-adm and all upstream profiles in one
package.  The optional tuned-gtk GUI, the power-profiles-daemon compatibility
daemon (tuned-ppd) and the extra profile subpackages are not built: they need
packages Tenko does not carry yet (pycairo, powertop, pyinotify).

%prep
%setup -q -n %{name}-%{version}

%build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} BINDIR=/usr/bin SBINDIR=/usr/sbin \
    DOCDIR=/usr/share/doc/tuned PYTHON=/usr/bin/python3 \
    TUNED_USER_PROFILES_DIR=/etc/tuned/profiles \
    TUNED_SYSTEM_PROFILES_DIR=/usr/lib/tuned/profiles

# The optional GUI is a separate subpackage upstream; without the Gtk
# typelibs and pycairo it would install a launcher that cannot start.
rm -f %{buildroot}/usr/sbin/tuned-gui
rm -f %{buildroot}/usr/share/applications/tuned-gui.desktop
rm -f %{buildroot}/usr/share/man/man8/tuned-gui.8
rm -f %{buildroot}/usr/share/tuned/ui/tuned-gui.glade
rmdir %{buildroot}/usr/share/tuned/ui 2>/dev/null || :

# The systemtap profiling helpers are a separate upstream subpackage and
# need /usr/bin/stap, which Tenko does not ship.  Keeping them in the main
# package would make it uninstallable.
rm -f %{buildroot}/usr/sbin/diskdevstat
rm -f %{buildroot}/usr/sbin/netdevstat
rm -f %{buildroot}/usr/sbin/scomes
rm -f %{buildroot}/usr/sbin/varnetload
rm -f %{buildroot}/usr/share/man/man8/diskdevstat.8
rm -f %{buildroot}/usr/share/man/man8/netdevstat.8
rm -f %{buildroot}/usr/share/man/man8/scomes.8
rm -f %{buildroot}/usr/share/man/man8/varnetload.8

# systemd preset that enables the daemon on install and upgrade.
install -Dm0644 %{_sourcedir}/tuned.preset \
    %{buildroot}/usr/lib/systemd/system-preset/40-tenko-tuned.preset

# The Makefile installs into Python's purelib (/usr/lib/python3.15); Tenko
# keeps site-packages under /usr/lib64.
if [ -d %{buildroot}/usr/lib/python3.15 ]; then
  mkdir -p %{buildroot}/usr/lib64
  mv %{buildroot}/usr/lib/python3.15 %{buildroot}/usr/lib64/
fi

%post
if [ -x /usr/bin/systemctl ]; then
    systemctl preset tuned.service >/dev/null 2>&1 || :
fi
# Older installs stored the active profile as a full path; normalise it.
if [ -f /etc/tuned/active_profile ]; then
    sed -i 's|.*/\([^/]\+\)/[^\.]\+\.conf|\1|' /etc/tuned/active_profile || :
fi

%preun
if [ "$1" -eq 0 ] && [ -x /usr/bin/systemctl ]; then
    systemctl stop tuned.service >/dev/null 2>&1 || :
    systemctl disable tuned.service >/dev/null 2>&1 || :
fi

%files -f %{_sourcedir}/tuned.filelist

%changelog
* Tue Nov 10 2026 tenko <build@tenko.invalid> 2.28.0-1
- New package: TuneD 2.28.0 (latest stable upstream, released 2026-08-22).
  Built from the upstream GitHub archive for the v2.28.0 tag because the
  release page has no source asset.
- The daemon, tuned-adm, the systemd/D-Bus/polkit integration, the kernel
  install hook and all upstream profiles are included in one package; the
  profiles subpackages are not split out.
- The optional tuned-gtk GUI, the tuned-ppd compatibility daemon and the
  extra profile subpackages are not built because pycairo, powertop and
  pyinotify are not packaged.  Python site-packages are moved to /usr/lib64.
- The systemtap profiling helpers (tuned-utils-systemtap upstream) are
  omitted: they need /usr/bin/stap, which Tenko does not ship.
- The bootloader helper is installed as /etc/grub.d/00_tuned (upstream
  moves it to /usr/share/tuned/grub2 for arches without grub2) so the
  bootloader plugin finds it on Tenko.
