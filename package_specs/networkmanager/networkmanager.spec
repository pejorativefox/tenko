Name:       NetworkManager
Version:    1.58.1
Release:    3
Summary:    Network configuration tool suite.
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
URL:        https://networkmanager.dev/
Prefix:     /usr
Source0:    NetworkManager-%{version}.tar.xz
Source1:    NetworkManager.conf
Source2:    org.freedesktop.NetworkManager.rules
Source3:    networkmanager-service.conf
Requires: shadow >= 4.6-1
Requires: wpa-supplicant
Provides: pkgconfig(libnm)

%description
NetworkManager is the standard Linux network configuration tool suite.

%prep
%setup

%build
sed '/initrd/d' -i src/meson.build
grep -rl '^#!.*python$' | xargs sed -i '1s/python/&3/'
mkdir build
pushd build
meson setup ..                    \
      --prefix=/usr               \
      --buildtype=release         \
      -D libaudit=no              \
      -D nmtui=true               \
      -D ovs=false                \
      -D ppp=false                \
      -D nbft=false               \
      -D selinux=false            \
      -D qt=false                 \
      -D session_tracking=systemd \
      -D nm_cloud_setup=false     \
      -D clat=false               \
      -D modem_manager=false \
      -D introspection=false
ninja
popd

%install    
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

rm -vf %{buildroot}%{_infodir}/dir*

# configuration
mkdir -pv %{buildroot}/etc/NetworkManager
cp %{SOURCE1} %{buildroot}/etc/NetworkManager/

# polkit policy
mkdir -pv %{buildroot}/usr/share/polkit-1/rules.d/
cp %{SOURCE2} %{buildroot}/usr/share/polkit-1/rules.d/

# finit service file
mkdir -pv %{buildroot}/etc/finit.d/available/
cp %{SOURCE3} %{buildroot}/etc/finit.d/available/networkmanager.conf

# Enable NetworkManager and disable systemd-networkd.  The preset sorts
# before systemd's 90-systemd.preset so its first-match rule wins over the
# networkd enable there.
install -vdm755 %{buildroot}/usr/lib/systemd/system-preset
install -vm644 %{_sourcedir}/40-tenko-networkmanager.preset \
    %{buildroot}/usr/lib/systemd/system-preset/40-tenko-networkmanager.preset


%post
groupadd -fg 86 netdev

# Presets are applied during image assembly, but a plain `dnf install` or
# upgrade on an existing system does not run preset-all.  Switch the live
# system over explicitly so NetworkManager starts and networkd stops
# managing the same links.
if [ -x /usr/bin/systemctl ]; then
    /usr/bin/systemctl --root=/ enable \
        NetworkManager.service NetworkManager-wait-online.service \
        >/dev/null 2>&1 || :
    /usr/bin/systemctl --root=/ disable \
        systemd-networkd.service systemd-networkd.socket \
        systemd-networkd-wait-online.service \
        systemd-networkd-resolve-hook.socket \
        systemd-networkd-varlink.socket \
        systemd-networkd-varlink-metrics.socket \
        >/dev/null 2>&1 || :
fi

%files -f %{_sourcedir}/networkmanager.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 1.58.1-3
- Require wpa-supplicant so installing NetworkManager brings the wireless
  supplicant the Wi-Fi backend needs.
- Ship 40-tenko-networkmanager.preset: enable NetworkManager and its
  wait-online unit, disable systemd-networkd and its sockets, so the two
  managers never fight over the same interfaces.  It sorts before
  systemd's 90-systemd.preset because the first matching preset rule wins.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.58.1-2
- Record the verified license (GPL-2.0-or-later AND LGPL-2.1-or-later): RELICENSE.md (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.58.1-1
- Sync with the base set

* Fri Jun 16 2023 Chris Statzer <chris.statzer@gmail.com> 1.42.4
- Changed the name of the finit service file.

* Thu May 14 2020 Chris Statzer <chris.statzer@qq.com> 1.14.6
- Moved old cat file kludges out, added finit service
