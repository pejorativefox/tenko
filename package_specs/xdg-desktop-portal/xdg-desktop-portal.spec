Name:       xdg-desktop-portal
Version:    1.22.1
Release:    2
Summary:    Desktop integration portal 
License:    LGPL-2.1-or-later AND LGPL-2.0-or-later AND GPL-2.0-or-later
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Desktop integration portal 

%prep
%setup

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -D tests=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files
/usr/lib/systemd/user/xdg-desktop-portal-rewrite-launchers.service
/usr/lib/systemd/user/xdg-desktop-portal.service
/usr/lib/systemd/user/xdg-document-portal.service
/usr/lib/systemd/user/xdg-permission-store.service
/usr/libexec/xdg-desktop-portal
/usr/libexec/xdg-desktop-portal-rewrite-launchers
/usr/libexec/xdg-desktop-portal-validate-icon
/usr/libexec/xdg-desktop-portal-validate-sound
/usr/libexec/xdg-document-portal
/usr/libexec/xdg-permission-store
/usr/share/dbus-1/interfaces/org.freedesktop.host.portal.Registry.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Access.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Account.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.AppChooser.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Background.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Clipboard.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.DynamicLauncher.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Email.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.FileChooser.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.GlobalShortcuts.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Inhibit.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.InputCapture.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Lockdown.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Notification.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.PermissionStore.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Print.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.RemoteDesktop.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Request.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.ScreenCast.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Screenshot.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Secret.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Session.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Settings.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Usb.xml
/usr/share/dbus-1/interfaces/org.freedesktop.impl.portal.Wallpaper.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Account.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Background.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Camera.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Clipboard.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Documents.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.DynamicLauncher.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Email.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.FileChooser.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.FileTransfer.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.GameMode.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.GlobalShortcuts.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Inhibit.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.InputCapture.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Location.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.MemoryMonitor.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.NetworkMonitor.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Notification.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.OpenURI.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.PowerProfileMonitor.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Print.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.ProxyResolver.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Realtime.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.RemoteDesktop.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Request.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.ScreenCast.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Screenshot.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Secret.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Session.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Settings.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Trash.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Usb.xml
/usr/share/dbus-1/interfaces/org.freedesktop.portal.Wallpaper.xml
/usr/share/dbus-1/services/org.freedesktop.impl.portal.PermissionStore.service
/usr/share/dbus-1/services/org.freedesktop.portal.Desktop.service
/usr/share/dbus-1/services/org.freedesktop.portal.Documents.service
/usr/share/locale/ar/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/be/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/bg/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/ca/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/cs/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/da/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/de/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/en_GB/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/es/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/fr/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/gl/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/he/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/hi/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/hr/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/hu/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/id/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/ie/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/it/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/ja/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/ka/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/kk/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/lt/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/nl/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/oc/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/pl/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/pt/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/pt_BR/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/ro/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/ru/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/sk/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/sl/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/sr/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/sr@latin/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/sv/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/tr/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/uk/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/zh_CN/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/locale/zh_TW/LC_MESSAGES/xdg-desktop-portal.mo
/usr/share/man/man5/portals.conf.5.gz
/usr/share/pkgconfig/xdg-desktop-portal.pc

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.22.1-2
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later AND LGPL-2.0-or-later AND GPL-2.0-or-later): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.22.1-1
- Sync with the base set

* Wed Jan 13 2021 Chris Statzer <chris.statzer@qq.com> 1.8.0
- Initial RPM

