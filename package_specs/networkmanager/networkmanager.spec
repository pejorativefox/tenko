Name:       NetworkManager
Version:    1.58.1
Release:    2
Summary:    Network configuration tool suite.
License:    GPL-2.0-or-later AND LGPL-2.1-or-later
Prefix:     /usr
Source0:    NetworkManager-%{version}.tar.xz
Source1:    NetworkManager.conf
Source2:    org.freedesktop.NetworkManager.rules
Source3:    networkmanager-service.conf
Requires: shadow >= 4.6-1
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


%post
groupadd -fg 86 netdev

%files
/etc/NetworkManager/NetworkManager.conf
/etc/finit.d/available/networkmanager.conf
/usr/bin/nm-online
/usr/bin/nmcli
/usr/bin/nmtui
/usr/bin/nmtui-connect
/usr/bin/nmtui-edit
/usr/bin/nmtui-hostname
/usr/include/libnm/NetworkManager.h
/usr/include/libnm/nm-access-point.h
/usr/include/libnm/nm-active-connection.h
/usr/include/libnm/nm-autoptr.h
/usr/include/libnm/nm-checkpoint.h
/usr/include/libnm/nm-client.h
/usr/include/libnm/nm-conn-utils.h
/usr/include/libnm/nm-connection.h
/usr/include/libnm/nm-core-enum-types.h
/usr/include/libnm/nm-core-types.h
/usr/include/libnm/nm-dbus-interface.h
/usr/include/libnm/nm-device-6lowpan.h
/usr/include/libnm/nm-device-adsl.h
/usr/include/libnm/nm-device-bond.h
/usr/include/libnm/nm-device-bridge.h
/usr/include/libnm/nm-device-bt.h
/usr/include/libnm/nm-device-dummy.h
/usr/include/libnm/nm-device-ethernet.h
/usr/include/libnm/nm-device-generic.h
/usr/include/libnm/nm-device-geneve.h
/usr/include/libnm/nm-device-hsr.h
/usr/include/libnm/nm-device-infiniband.h
/usr/include/libnm/nm-device-ip-tunnel.h
/usr/include/libnm/nm-device-ipvlan.h
/usr/include/libnm/nm-device-loopback.h
/usr/include/libnm/nm-device-macsec.h
/usr/include/libnm/nm-device-macvlan.h
/usr/include/libnm/nm-device-modem.h
/usr/include/libnm/nm-device-olpc-mesh.h
/usr/include/libnm/nm-device-ovs-bridge.h
/usr/include/libnm/nm-device-ovs-interface.h
/usr/include/libnm/nm-device-ovs-port.h
/usr/include/libnm/nm-device-ppp.h
/usr/include/libnm/nm-device-team.h
/usr/include/libnm/nm-device-tun.h
/usr/include/libnm/nm-device-veth.h
/usr/include/libnm/nm-device-vlan.h
/usr/include/libnm/nm-device-vrf.h
/usr/include/libnm/nm-device-vxlan.h
/usr/include/libnm/nm-device-wifi-p2p.h
/usr/include/libnm/nm-device-wifi.h
/usr/include/libnm/nm-device-wimax.h
/usr/include/libnm/nm-device-wireguard.h
/usr/include/libnm/nm-device-wpan.h
/usr/include/libnm/nm-device.h
/usr/include/libnm/nm-dhcp-config.h
/usr/include/libnm/nm-enum-types.h
/usr/include/libnm/nm-errors.h
/usr/include/libnm/nm-ethtool-utils.h
/usr/include/libnm/nm-ip-config.h
/usr/include/libnm/nm-keyfile.h
/usr/include/libnm/nm-object.h
/usr/include/libnm/nm-remote-connection.h
/usr/include/libnm/nm-secret-agent-old.h
/usr/include/libnm/nm-setting-6lowpan.h
/usr/include/libnm/nm-setting-8021x.h
/usr/include/libnm/nm-setting-adsl.h
/usr/include/libnm/nm-setting-bluetooth.h
/usr/include/libnm/nm-setting-bond-port.h
/usr/include/libnm/nm-setting-bond.h
/usr/include/libnm/nm-setting-bridge-port.h
/usr/include/libnm/nm-setting-bridge.h
/usr/include/libnm/nm-setting-cdma.h
/usr/include/libnm/nm-setting-connection.h
/usr/include/libnm/nm-setting-dcb.h
/usr/include/libnm/nm-setting-dummy.h
/usr/include/libnm/nm-setting-ethtool.h
/usr/include/libnm/nm-setting-generic.h
/usr/include/libnm/nm-setting-geneve.h
/usr/include/libnm/nm-setting-gsm.h
/usr/include/libnm/nm-setting-hostname.h
/usr/include/libnm/nm-setting-hsr.h
/usr/include/libnm/nm-setting-infiniband.h
/usr/include/libnm/nm-setting-ip-config.h
/usr/include/libnm/nm-setting-ip-tunnel.h
/usr/include/libnm/nm-setting-ip4-config.h
/usr/include/libnm/nm-setting-ip6-config.h
/usr/include/libnm/nm-setting-ipvlan.h
/usr/include/libnm/nm-setting-link.h
/usr/include/libnm/nm-setting-loopback.h
/usr/include/libnm/nm-setting-macsec.h
/usr/include/libnm/nm-setting-macvlan.h
/usr/include/libnm/nm-setting-match.h
/usr/include/libnm/nm-setting-olpc-mesh.h
/usr/include/libnm/nm-setting-ovs-bridge.h
/usr/include/libnm/nm-setting-ovs-dpdk.h
/usr/include/libnm/nm-setting-ovs-external-ids.h
/usr/include/libnm/nm-setting-ovs-interface.h
/usr/include/libnm/nm-setting-ovs-other-config.h
/usr/include/libnm/nm-setting-ovs-patch.h
/usr/include/libnm/nm-setting-ovs-port.h
/usr/include/libnm/nm-setting-ppp.h
/usr/include/libnm/nm-setting-pppoe.h
/usr/include/libnm/nm-setting-prefix-delegation.h
/usr/include/libnm/nm-setting-proxy.h
/usr/include/libnm/nm-setting-serial.h
/usr/include/libnm/nm-setting-sriov.h
/usr/include/libnm/nm-setting-tc-config.h
/usr/include/libnm/nm-setting-team-port.h
/usr/include/libnm/nm-setting-team.h
/usr/include/libnm/nm-setting-tun.h
/usr/include/libnm/nm-setting-user.h
/usr/include/libnm/nm-setting-veth.h
/usr/include/libnm/nm-setting-vlan.h
/usr/include/libnm/nm-setting-vpn.h
/usr/include/libnm/nm-setting-vrf.h
/usr/include/libnm/nm-setting-vxlan.h
/usr/include/libnm/nm-setting-wifi-p2p.h
/usr/include/libnm/nm-setting-wimax.h
/usr/include/libnm/nm-setting-wired.h
/usr/include/libnm/nm-setting-wireguard.h
/usr/include/libnm/nm-setting-wireless-security.h
/usr/include/libnm/nm-setting-wireless.h
/usr/include/libnm/nm-setting-wpan.h
/usr/include/libnm/nm-setting.h
/usr/include/libnm/nm-simple-connection.h
/usr/include/libnm/nm-utils.h
/usr/include/libnm/nm-version-macros.h
/usr/include/libnm/nm-version.h
/usr/include/libnm/nm-vpn-connection.h
/usr/include/libnm/nm-vpn-dbus-interface.h
/usr/include/libnm/nm-vpn-editor-plugin.h
/usr/include/libnm/nm-vpn-editor.h
/usr/include/libnm/nm-vpn-plugin-info.h
/usr/include/libnm/nm-vpn-plugin-old.h
/usr/include/libnm/nm-vpn-service-plugin.h
/usr/include/libnm/nm-wifi-p2p-peer.h
/usr/include/libnm/nm-wimax-nsp.h
/usr/lib/firewalld/zones/nm-shared.xml
/usr/lib/systemd/system/NetworkManager-config-initrd.service
/usr/lib/systemd/system/NetworkManager-dispatcher.service
/usr/lib/systemd/system/NetworkManager-initrd.service
/usr/lib/systemd/system/NetworkManager-wait-online-initrd.service
/usr/lib/systemd/system/NetworkManager-wait-online.service
/usr/lib/systemd/system/NetworkManager.service
/usr/lib/systemd/system/nm-priv-helper.service
/usr/lib/udev/rules.d/84-nm-drivers.rules
/usr/lib/udev/rules.d/85-nm-unmanaged.rules
/usr/lib/udev/rules.d/90-nm-thunderbolt.rules
/usr/lib64/NetworkManager/1.58.1/libnm-device-plugin-adsl.so
/usr/lib64/NetworkManager/1.58.1/libnm-device-plugin-wifi.so
/usr/lib64/libnm.so
/usr/lib64/libnm.so.0
/usr/lib64/libnm.so.0.1.0
/usr/lib64/pkgconfig/libnm.pc
/usr/libexec/nm-daemon-helper
/usr/libexec/nm-dhcp-helper
/usr/libexec/nm-dispatcher
/usr/libexec/nm-libnm-helper
/usr/libexec/nm-priv-helper
/usr/sbin/NetworkManager
/usr/share/bash-completion/completions/nmcli
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.AccessPoint.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.AgentManager.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Checkpoint.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Connection.Active.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.DHCP4Config.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.DHCP6Config.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Adsl.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Bluetooth.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Bond.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Bridge.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Dummy.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Generic.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Geneve.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Hsr.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.IPTunnel.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Infiniband.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Ipvlan.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Loopback.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Lowpan.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Macsec.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Macvlan.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Modem.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.OlpcMesh.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.OvsBridge.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.OvsInterface.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.OvsPort.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Ppp.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Statistics.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Team.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Tun.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Veth.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Vlan.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Vrf.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Vxlan.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.WiMax.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.WifiP2P.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.WireGuard.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Wired.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Wireless.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.Wpan.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Device.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.DnsManager.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.IP4Config.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.IP6Config.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.PPP.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.SecretAgent.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Settings.Connection.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.Settings.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.VPN.Connection.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.VPN.Plugin.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.WiMax.Nsp.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.WifiP2PPeer.xml
/usr/share/dbus-1/interfaces/org.freedesktop.NetworkManager.xml
/usr/share/dbus-1/system-services/org.freedesktop.nm_dispatcher.service
/usr/share/dbus-1/system-services/org.freedesktop.nm_priv_helper.service
/usr/share/dbus-1/system.d/nm-dispatcher.conf
/usr/share/dbus-1/system.d/nm-priv-helper.conf
/usr/share/dbus-1/system.d/org.freedesktop.NetworkManager.conf
/usr/share/doc/NetworkManager/examples/server.conf
/usr/share/locale/as/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/be@latin/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/bg/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/bn_IN/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/bs/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/ca/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/cs/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/da/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/de/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/dz/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/el/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/en_CA/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/en_GB/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/eo/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/es/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/et/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/eu/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/fi/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/fr/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/gd/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/gl/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/gu/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/he/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/hi/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/hr/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/hu/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/id/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/it/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/ja/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/ka/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/kk/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/kn/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/ko/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/ku/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/lt/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/lv/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/mk/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/ml/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/mr/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/nb/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/ne/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/nl/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/oc/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/or/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/pa/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/pl/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/pt/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/pt_BR/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/ro/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/ru/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/rw/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/sk/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/sl/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/sq/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/sr/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/sr@latin/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/sv/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/ta/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/te/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/th/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/tr/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/uk/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/vi/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/wa/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/zh_CN/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/zh_HK/LC_MESSAGES/NetworkManager.mo
/usr/share/locale/zh_TW/LC_MESSAGES/NetworkManager.mo
/usr/share/man/man1/nm-online.1.gz
/usr/share/man/man1/nmcli.1.gz
/usr/share/man/man1/nmtui-connect.1.gz
/usr/share/man/man1/nmtui-edit.1.gz
/usr/share/man/man1/nmtui-hostname.1.gz
/usr/share/man/man1/nmtui.1.gz
/usr/share/man/man5/NetworkManager.conf.5.gz
/usr/share/man/man5/nm-settings-dbus.5.gz
/usr/share/man/man5/nm-settings-keyfile.5.gz
/usr/share/man/man5/nm-settings-nmcli.5.gz
/usr/share/man/man5/nm-settings.5.gz
/usr/share/man/man5/nm-system-settings.conf.5.gz
/usr/share/man/man7/nmcli-examples.7.gz
/usr/share/man/man8/NetworkManager-dispatcher.8.gz
/usr/share/man/man8/NetworkManager-wait-online.service.8.gz
/usr/share/man/man8/NetworkManager.8.gz
/usr/share/man/man8/nm-initrd-generator.8.gz
/usr/share/polkit-1/actions/org.freedesktop.NetworkManager.policy
/usr/share/polkit-1/rules.d/org.freedesktop.NetworkManager.rules

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.58.1-2
- Record the verified license (GPL-2.0-or-later AND LGPL-2.1-or-later): RELICENSE.md (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.58.1-1
- Sync with BLFS r13.1

* Fri Jun 16 2023 Chris Statzer <chris.statzer@gmail.com> 1.42.4
- Changed the name of the finit service file.

* Thu May 14 2020 Chris Statzer <chris.statzer@qq.com> 1.14.6
- Moved old cat file kludges out, added finit service
