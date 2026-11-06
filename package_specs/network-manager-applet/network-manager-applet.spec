Name:       network-manager-applet
Version:    1.34.0
Release:    2
Summary:    NetworkManager GUI applet and connection editor
License:    GPL-2.0-or-later
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
nm-applet is a GTK-based GUI applet to monitor network status and devices
and to start and stop network connections managed by NetworkManager. The
package also includes the nm-connection-editor connection editor.

%prep
%setup -a 0

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -D appindicator=no  \
      -D selinux=false    \
      -D team=false       \
      -D wwan=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
# libnma ships the same schema (both tarballs install it); keep the
# library as owner so the two packages do not conflict.
rm -f %{buildroot}/usr/share/glib-2.0/schemas/org.gnome.nm-applet.gschema.xml
rm -vf %{buildroot}%{_infodir}/dir

%files
/etc/xdg/autostart/nm-applet.desktop
/usr/bin/nm-applet
/usr/bin/nm-connection-editor
/usr/share/GConf/gsettings/nm-applet.convert
/usr/share/applications/nm-applet.desktop
/usr/share/applications/nm-connection-editor.desktop
/usr/share/icons/hicolor/16x16/apps/nm-device-wired.png
/usr/share/icons/hicolor/16x16/apps/nm-no-connection.png
/usr/share/icons/hicolor/16x16/apps/nm-vpn-standalone-lock.png
/usr/share/icons/hicolor/22x22/apps/nm-adhoc.png
/usr/share/icons/hicolor/22x22/apps/nm-device-wired-secure.png
/usr/share/icons/hicolor/22x22/apps/nm-device-wired.png
/usr/share/icons/hicolor/22x22/apps/nm-device-wwan.png
/usr/share/icons/hicolor/22x22/apps/nm-insecure-warn.png
/usr/share/icons/hicolor/22x22/apps/nm-mb-roam.png
/usr/share/icons/hicolor/22x22/apps/nm-no-connection.png
/usr/share/icons/hicolor/22x22/apps/nm-secure-lock.png
/usr/share/icons/hicolor/22x22/apps/nm-signal-00-secure.png
/usr/share/icons/hicolor/22x22/apps/nm-signal-00.png
/usr/share/icons/hicolor/22x22/apps/nm-signal-100-secure.png
/usr/share/icons/hicolor/22x22/apps/nm-signal-100.png
/usr/share/icons/hicolor/22x22/apps/nm-signal-25-secure.png
/usr/share/icons/hicolor/22x22/apps/nm-signal-25.png
/usr/share/icons/hicolor/22x22/apps/nm-signal-50-secure.png
/usr/share/icons/hicolor/22x22/apps/nm-signal-50.png
/usr/share/icons/hicolor/22x22/apps/nm-signal-75-secure.png
/usr/share/icons/hicolor/22x22/apps/nm-signal-75.png
/usr/share/icons/hicolor/22x22/apps/nm-stage01-connecting01.png
/usr/share/icons/hicolor/22x22/apps/nm-stage01-connecting02.png
/usr/share/icons/hicolor/22x22/apps/nm-stage01-connecting03.png
/usr/share/icons/hicolor/22x22/apps/nm-stage01-connecting04.png
/usr/share/icons/hicolor/22x22/apps/nm-stage01-connecting05.png
/usr/share/icons/hicolor/22x22/apps/nm-stage01-connecting06.png
/usr/share/icons/hicolor/22x22/apps/nm-stage01-connecting07.png
/usr/share/icons/hicolor/22x22/apps/nm-stage01-connecting08.png
/usr/share/icons/hicolor/22x22/apps/nm-stage01-connecting09.png
/usr/share/icons/hicolor/22x22/apps/nm-stage01-connecting10.png
/usr/share/icons/hicolor/22x22/apps/nm-stage01-connecting11.png
/usr/share/icons/hicolor/22x22/apps/nm-stage02-connecting01.png
/usr/share/icons/hicolor/22x22/apps/nm-stage02-connecting02.png
/usr/share/icons/hicolor/22x22/apps/nm-stage02-connecting03.png
/usr/share/icons/hicolor/22x22/apps/nm-stage02-connecting04.png
/usr/share/icons/hicolor/22x22/apps/nm-stage02-connecting05.png
/usr/share/icons/hicolor/22x22/apps/nm-stage02-connecting06.png
/usr/share/icons/hicolor/22x22/apps/nm-stage02-connecting07.png
/usr/share/icons/hicolor/22x22/apps/nm-stage02-connecting08.png
/usr/share/icons/hicolor/22x22/apps/nm-stage02-connecting09.png
/usr/share/icons/hicolor/22x22/apps/nm-stage02-connecting10.png
/usr/share/icons/hicolor/22x22/apps/nm-stage02-connecting11.png
/usr/share/icons/hicolor/22x22/apps/nm-stage03-connecting01.png
/usr/share/icons/hicolor/22x22/apps/nm-stage03-connecting02.png
/usr/share/icons/hicolor/22x22/apps/nm-stage03-connecting03.png
/usr/share/icons/hicolor/22x22/apps/nm-stage03-connecting04.png
/usr/share/icons/hicolor/22x22/apps/nm-stage03-connecting05.png
/usr/share/icons/hicolor/22x22/apps/nm-stage03-connecting06.png
/usr/share/icons/hicolor/22x22/apps/nm-stage03-connecting07.png
/usr/share/icons/hicolor/22x22/apps/nm-stage03-connecting08.png
/usr/share/icons/hicolor/22x22/apps/nm-stage03-connecting09.png
/usr/share/icons/hicolor/22x22/apps/nm-stage03-connecting10.png
/usr/share/icons/hicolor/22x22/apps/nm-stage03-connecting11.png
/usr/share/icons/hicolor/22x22/apps/nm-tech-3g.png
/usr/share/icons/hicolor/22x22/apps/nm-tech-cdma-1x.png
/usr/share/icons/hicolor/22x22/apps/nm-tech-edge.png
/usr/share/icons/hicolor/22x22/apps/nm-tech-evdo.png
/usr/share/icons/hicolor/22x22/apps/nm-tech-gprs.png
/usr/share/icons/hicolor/22x22/apps/nm-tech-hspa.png
/usr/share/icons/hicolor/22x22/apps/nm-tech-lte.png
/usr/share/icons/hicolor/22x22/apps/nm-tech-umts.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-active-lock.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting01.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting02.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting03.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting04.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting05.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting06.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting07.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting08.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting09.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting10.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting11.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting12.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting13.png
/usr/share/icons/hicolor/22x22/apps/nm-vpn-connecting14.png
/usr/share/icons/hicolor/22x22/apps/nm-wwan-tower.png
/usr/share/icons/hicolor/32x32/apps/nm-device-wired.png
/usr/share/icons/hicolor/32x32/apps/nm-no-connection.png
/usr/share/icons/hicolor/48x48/apps/nm-device-wireless.png
/usr/share/icons/hicolor/scalable/apps/nm-device-wired-secure-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-device-wired-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-device-wired.svg
/usr/share/icons/hicolor/scalable/apps/nm-device-wwan-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-no-connection-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-no-connection.svg
/usr/share/icons/hicolor/scalable/apps/nm-signal-00-secure-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-signal-00-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-signal-100-secure-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-signal-100-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-signal-25-secure-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-signal-25-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-signal-50-secure-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-signal-50-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-signal-75-secure-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-signal-75-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-active-lock-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting01-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting02-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting03-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting04-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting05-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting06-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting07-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting08-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting09-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting10-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting11-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting12-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting13-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-connecting14-symbolic.svg
/usr/share/icons/hicolor/scalable/apps/nm-vpn-standalone-lock-symbolic.svg
/usr/share/locale/af/LC_MESSAGES/nm-applet.mo
/usr/share/locale/an/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ar/LC_MESSAGES/nm-applet.mo
/usr/share/locale/as/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ast/LC_MESSAGES/nm-applet.mo
/usr/share/locale/be/LC_MESSAGES/nm-applet.mo
/usr/share/locale/be@latin/LC_MESSAGES/nm-applet.mo
/usr/share/locale/bg/LC_MESSAGES/nm-applet.mo
/usr/share/locale/bn_IN/LC_MESSAGES/nm-applet.mo
/usr/share/locale/bs/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ca/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ca@valencia/LC_MESSAGES/nm-applet.mo
/usr/share/locale/crh/LC_MESSAGES/nm-applet.mo
/usr/share/locale/cs/LC_MESSAGES/nm-applet.mo
/usr/share/locale/da/LC_MESSAGES/nm-applet.mo
/usr/share/locale/de/LC_MESSAGES/nm-applet.mo
/usr/share/locale/dz/LC_MESSAGES/nm-applet.mo
/usr/share/locale/el/LC_MESSAGES/nm-applet.mo
/usr/share/locale/en_CA/LC_MESSAGES/nm-applet.mo
/usr/share/locale/en_GB/LC_MESSAGES/nm-applet.mo
/usr/share/locale/eo/LC_MESSAGES/nm-applet.mo
/usr/share/locale/es/LC_MESSAGES/nm-applet.mo
/usr/share/locale/et/LC_MESSAGES/nm-applet.mo
/usr/share/locale/eu/LC_MESSAGES/nm-applet.mo
/usr/share/locale/fa/LC_MESSAGES/nm-applet.mo
/usr/share/locale/fi/LC_MESSAGES/nm-applet.mo
/usr/share/locale/fr/LC_MESSAGES/nm-applet.mo
/usr/share/locale/gd/LC_MESSAGES/nm-applet.mo
/usr/share/locale/gl/LC_MESSAGES/nm-applet.mo
/usr/share/locale/gu/LC_MESSAGES/nm-applet.mo
/usr/share/locale/he/LC_MESSAGES/nm-applet.mo
/usr/share/locale/hi/LC_MESSAGES/nm-applet.mo
/usr/share/locale/hr/LC_MESSAGES/nm-applet.mo
/usr/share/locale/hu/LC_MESSAGES/nm-applet.mo
/usr/share/locale/id/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ie/LC_MESSAGES/nm-applet.mo
/usr/share/locale/is/LC_MESSAGES/nm-applet.mo
/usr/share/locale/it/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ja/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ka/LC_MESSAGES/nm-applet.mo
/usr/share/locale/kk/LC_MESSAGES/nm-applet.mo
/usr/share/locale/km/LC_MESSAGES/nm-applet.mo
/usr/share/locale/kn/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ko/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ku/LC_MESSAGES/nm-applet.mo
/usr/share/locale/lt/LC_MESSAGES/nm-applet.mo
/usr/share/locale/lv/LC_MESSAGES/nm-applet.mo
/usr/share/locale/mk/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ml/LC_MESSAGES/nm-applet.mo
/usr/share/locale/mr/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ms/LC_MESSAGES/nm-applet.mo
/usr/share/locale/nb/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ne/LC_MESSAGES/nm-applet.mo
/usr/share/locale/nl/LC_MESSAGES/nm-applet.mo
/usr/share/locale/nn/LC_MESSAGES/nm-applet.mo
/usr/share/locale/oc/LC_MESSAGES/nm-applet.mo
/usr/share/locale/or/LC_MESSAGES/nm-applet.mo
/usr/share/locale/pa/LC_MESSAGES/nm-applet.mo
/usr/share/locale/pl/LC_MESSAGES/nm-applet.mo
/usr/share/locale/pt/LC_MESSAGES/nm-applet.mo
/usr/share/locale/pt_BR/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ro/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ru/LC_MESSAGES/nm-applet.mo
/usr/share/locale/rw/LC_MESSAGES/nm-applet.mo
/usr/share/locale/sk/LC_MESSAGES/nm-applet.mo
/usr/share/locale/sl/LC_MESSAGES/nm-applet.mo
/usr/share/locale/sq/LC_MESSAGES/nm-applet.mo
/usr/share/locale/sr/LC_MESSAGES/nm-applet.mo
/usr/share/locale/sr@latin/LC_MESSAGES/nm-applet.mo
/usr/share/locale/sv/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ta/LC_MESSAGES/nm-applet.mo
/usr/share/locale/te/LC_MESSAGES/nm-applet.mo
/usr/share/locale/tg/LC_MESSAGES/nm-applet.mo
/usr/share/locale/th/LC_MESSAGES/nm-applet.mo
/usr/share/locale/tr/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ug/LC_MESSAGES/nm-applet.mo
/usr/share/locale/uk/LC_MESSAGES/nm-applet.mo
/usr/share/locale/ur/LC_MESSAGES/nm-applet.mo
/usr/share/locale/vi/LC_MESSAGES/nm-applet.mo
/usr/share/locale/wa/LC_MESSAGES/nm-applet.mo
/usr/share/locale/zh_CN/LC_MESSAGES/nm-applet.mo
/usr/share/locale/zh_HK/LC_MESSAGES/nm-applet.mo
/usr/share/locale/zh_TW/LC_MESSAGES/nm-applet.mo
/usr/share/man/man1/nm-applet.1.gz
/usr/share/man/man1/nm-connection-editor.1.gz
/usr/share/metainfo/nm-connection-editor.appdata.xml

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.34.0-2
- Replace the TODO summary/description and record the verified license
  (GPL-2.0-or-later): src/main.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.34.0-1
- Sync with the base set

# let's skip this for now

