Name:       wpa-supplicant
Version:    2.12
Release:    2
Summary:    WPA/WPA2 supplicant for wireless networks
License:    BSD-3-Clause
Prefix:     /usr
Source0:    wpa_supplicant-%{version}.tar.gz


%description
wpa_supplicant is a WPA Supplicant for Linux, BSD, Mac OS X and Windows with
support for WPA and WPA2 (IEEE 802.11i/RSN). It supports WPA-PSK and WPA
with EAP, including an integrated IEEE 802.1X supplicant.

%prep
%setup -a 0 -n wpa_supplicant-%{version}

%build
cat > wpa_supplicant/.config << "EOF"
CONFIG_BACKEND=file
CONFIG_CTRL_IFACE=y
CONFIG_DEBUG_FILE=y
CONFIG_DEBUG_SYSLOG=y
CONFIG_DEBUG_SYSLOG_FACILITY=LOG_DAEMON
CONFIG_DRIVER_NL80211=y
CONFIG_DRIVER_WEXT=y
CONFIG_DRIVER_WIRED=y
CONFIG_EAP_GTC=y
CONFIG_EAP_LEAP=y
CONFIG_EAP_MD5=y
CONFIG_EAP_MSCHAPV2=y
CONFIG_EAP_OTP=y
CONFIG_EAP_PEAP=y
CONFIG_EAP_TLS=y
CONFIG_EAP_TTLS=y
CONFIG_IEEE8021X_EAPOL=y
CONFIG_IPV6=y
CONFIG_LIBNL32=y
CONFIG_PEERKEY=y
CONFIG_PKCS12=y
CONFIG_READLINE=y
CONFIG_SMARTCARD=y
CONFIG_WPS=y
CONFIG_CTRL_IFACE_DBUS=y
CONFIG_CTRL_IFACE_DBUS_NEW=y
CONFIG_CTRL_IFACE_DBUS_INTRO=y
CFLAGS += -I/usr/include/libnl3
EOF

pushd wpa_supplicant
make BINDIR=/sbin LIBDIR=/lib
popd


%install    
rm -rf %{buildroot}
pushd wpa_supplicant
mkdir -pv %{buildroot}/sbin
install -v -m755 wpa_{cli,passphrase,supplicant} %{buildroot}/sbin/
# dbus
mkdir -pv %{buildroot}/usr/share/dbus-1/system-services/
install -v -m644 dbus/fi.w1.wpa_supplicant1.service %{buildroot}/usr/share/dbus-1/system-services/
install -v -d -m755 %{buildroot}/etc/dbus-1/system.d
install -v -m644 dbus/dbus-wpa_supplicant.conf %{buildroot}/etc/dbus-1/system.d/wpa_supplicant.conf
popd

%files
/etc/dbus-1/system.d/wpa_supplicant.conf
/sbin/wpa_cli
/sbin/wpa_passphrase
/sbin/wpa_supplicant
/usr/share/dbus-1/system-services/fi.w1.wpa_supplicant1.service

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 2.12-2
- Replace the TODO summary/description and record the verified license
  (BSD-3-Clause): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 2.12-1
- Sync with the base set

# let's skip this for now

