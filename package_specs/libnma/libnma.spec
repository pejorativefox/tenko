Name:       libnma
Version:    1.10.6
Release:    1
Summary:    NetworkManager GUI library
License:    LGPL-2.1
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
libnma provides a shared library used by NetworkManager's GUI clients
(GTK3 widgets for connection editing and secrets).

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                                  \
      --prefix=/usr                             \
      --buildtype=release                       \
      -D gtk_doc=false                          \
      -D libnma_gtk4=false                      \
      -D mobile_broadband_provider_info=false \
      -D introspection=false                    \
      -D vapi=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files
/usr/include/libnma/nma-bar-code-widget.h
/usr/include/libnma/nma-bar-code.h
/usr/include/libnma/nma-cert-chooser.h
/usr/include/libnma/nma-mobile-providers.h
/usr/include/libnma/nma-mobile-wizard.h
/usr/include/libnma/nma-ui-utils.h
/usr/include/libnma/nma-version.h
/usr/include/libnma/nma-vpn-password-dialog.h
/usr/include/libnma/nma-wifi-dialog.h
/usr/include/libnma/nma-ws-802-1x.h
/usr/include/libnma/nma-ws-dynamic-wep.h
/usr/include/libnma/nma-ws-leap.h
/usr/include/libnma/nma-ws-owe.h
/usr/include/libnma/nma-ws-sae.h
/usr/include/libnma/nma-ws-wep-key.h
/usr/include/libnma/nma-ws-wpa-eap.h
/usr/include/libnma/nma-ws-wpa-psk.h
/usr/include/libnma/nma-ws.h
/usr/lib64/libnma.so
/usr/lib64/libnma.so.0
/usr/lib64/libnma.so.0.0.0
/usr/lib64/pkgconfig/libnma.pc
/usr/share/glib-2.0/schemas/org.gnome.nm-applet.eap.gschema.xml
/usr/share/glib-2.0/schemas/org.gnome.nm-applet.gschema.xml
/usr/share/locale/af/LC_MESSAGES/libnma.mo
/usr/share/locale/an/LC_MESSAGES/libnma.mo
/usr/share/locale/ar/LC_MESSAGES/libnma.mo
/usr/share/locale/as/LC_MESSAGES/libnma.mo
/usr/share/locale/ast/LC_MESSAGES/libnma.mo
/usr/share/locale/be/LC_MESSAGES/libnma.mo
/usr/share/locale/be@latin/LC_MESSAGES/libnma.mo
/usr/share/locale/bg/LC_MESSAGES/libnma.mo
/usr/share/locale/bn_IN/LC_MESSAGES/libnma.mo
/usr/share/locale/bs/LC_MESSAGES/libnma.mo
/usr/share/locale/ca/LC_MESSAGES/libnma.mo
/usr/share/locale/ca@valencia/LC_MESSAGES/libnma.mo
/usr/share/locale/crh/LC_MESSAGES/libnma.mo
/usr/share/locale/cs/LC_MESSAGES/libnma.mo
/usr/share/locale/da/LC_MESSAGES/libnma.mo
/usr/share/locale/de/LC_MESSAGES/libnma.mo
/usr/share/locale/dz/LC_MESSAGES/libnma.mo
/usr/share/locale/el/LC_MESSAGES/libnma.mo
/usr/share/locale/en_CA/LC_MESSAGES/libnma.mo
/usr/share/locale/en_GB/LC_MESSAGES/libnma.mo
/usr/share/locale/eo/LC_MESSAGES/libnma.mo
/usr/share/locale/es/LC_MESSAGES/libnma.mo
/usr/share/locale/et/LC_MESSAGES/libnma.mo
/usr/share/locale/eu/LC_MESSAGES/libnma.mo
/usr/share/locale/fa/LC_MESSAGES/libnma.mo
/usr/share/locale/fi/LC_MESSAGES/libnma.mo
/usr/share/locale/fr/LC_MESSAGES/libnma.mo
/usr/share/locale/gd/LC_MESSAGES/libnma.mo
/usr/share/locale/gl/LC_MESSAGES/libnma.mo
/usr/share/locale/gu/LC_MESSAGES/libnma.mo
/usr/share/locale/he/LC_MESSAGES/libnma.mo
/usr/share/locale/hi/LC_MESSAGES/libnma.mo
/usr/share/locale/hr/LC_MESSAGES/libnma.mo
/usr/share/locale/hu/LC_MESSAGES/libnma.mo
/usr/share/locale/id/LC_MESSAGES/libnma.mo
/usr/share/locale/is/LC_MESSAGES/libnma.mo
/usr/share/locale/it/LC_MESSAGES/libnma.mo
/usr/share/locale/ja/LC_MESSAGES/libnma.mo
/usr/share/locale/ka/LC_MESSAGES/libnma.mo
/usr/share/locale/kk/LC_MESSAGES/libnma.mo
/usr/share/locale/km/LC_MESSAGES/libnma.mo
/usr/share/locale/kn/LC_MESSAGES/libnma.mo
/usr/share/locale/ko/LC_MESSAGES/libnma.mo
/usr/share/locale/ku/LC_MESSAGES/libnma.mo
/usr/share/locale/lt/LC_MESSAGES/libnma.mo
/usr/share/locale/lv/LC_MESSAGES/libnma.mo
/usr/share/locale/mk/LC_MESSAGES/libnma.mo
/usr/share/locale/ml/LC_MESSAGES/libnma.mo
/usr/share/locale/mr/LC_MESSAGES/libnma.mo
/usr/share/locale/ms/LC_MESSAGES/libnma.mo
/usr/share/locale/nb/LC_MESSAGES/libnma.mo
/usr/share/locale/ne/LC_MESSAGES/libnma.mo
/usr/share/locale/nl/LC_MESSAGES/libnma.mo
/usr/share/locale/nn/LC_MESSAGES/libnma.mo
/usr/share/locale/oc/LC_MESSAGES/libnma.mo
/usr/share/locale/or/LC_MESSAGES/libnma.mo
/usr/share/locale/pa/LC_MESSAGES/libnma.mo
/usr/share/locale/pl/LC_MESSAGES/libnma.mo
/usr/share/locale/pt/LC_MESSAGES/libnma.mo
/usr/share/locale/pt_BR/LC_MESSAGES/libnma.mo
/usr/share/locale/ro/LC_MESSAGES/libnma.mo
/usr/share/locale/ru/LC_MESSAGES/libnma.mo
/usr/share/locale/rw/LC_MESSAGES/libnma.mo
/usr/share/locale/sk/LC_MESSAGES/libnma.mo
/usr/share/locale/sl/LC_MESSAGES/libnma.mo
/usr/share/locale/sq/LC_MESSAGES/libnma.mo
/usr/share/locale/sr/LC_MESSAGES/libnma.mo
/usr/share/locale/sr@latin/LC_MESSAGES/libnma.mo
/usr/share/locale/sv/LC_MESSAGES/libnma.mo
/usr/share/locale/ta/LC_MESSAGES/libnma.mo
/usr/share/locale/te/LC_MESSAGES/libnma.mo
/usr/share/locale/tg/LC_MESSAGES/libnma.mo
/usr/share/locale/th/LC_MESSAGES/libnma.mo
/usr/share/locale/tr/LC_MESSAGES/libnma.mo
/usr/share/locale/ug/LC_MESSAGES/libnma.mo
/usr/share/locale/uk/LC_MESSAGES/libnma.mo
/usr/share/locale/ur/LC_MESSAGES/libnma.mo
/usr/share/locale/vi/LC_MESSAGES/libnma.mo
/usr/share/locale/wa/LC_MESSAGES/libnma.mo
/usr/share/locale/zh_CN/LC_MESSAGES/libnma.mo
/usr/share/locale/zh_HK/LC_MESSAGES/libnma.mo
/usr/share/locale/zh_TW/LC_MESSAGES/libnma.mo

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.10.6-1
- New package, required by network-manager-applet
