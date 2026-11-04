Name:       libportal 
Version:    0.9.1
Release:    1
Summary:    Flatpak portal library 
License:    GPL
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Flatpak portal library 

%prep
%setup

%build
mkdir build
pushd build
meson setup ..                 \
      --prefix=/usr            \
      --buildtype=release      \
      -D backend-gtk4=disabled \
      -D backend-qt5=disabled  \
      -D backend-qt6=disabled  \
      -D docs=false            \
      -D vapi=false            \
      -D tests=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files
/usr/include/libportal-gtk3/portal-gtk3.h
/usr/include/libportal/account.h
/usr/include/libportal/background.h
/usr/include/libportal/camera.h
/usr/include/libportal/dynamic-launcher.h
/usr/include/libportal/email.h
/usr/include/libportal/filechooser.h
/usr/include/libportal/glib-backports.h
/usr/include/libportal/inhibit.h
/usr/include/libportal/inputcapture-pointerbarrier.h
/usr/include/libportal/inputcapture-zone.h
/usr/include/libportal/inputcapture.h
/usr/include/libportal/location.h
/usr/include/libportal/notification.h
/usr/include/libportal/openuri.h
/usr/include/libportal/parent.h
/usr/include/libportal/portal-enums.h
/usr/include/libportal/portal-helpers.h
/usr/include/libportal/portal.h
/usr/include/libportal/print.h
/usr/include/libportal/remote.h
/usr/include/libportal/screenshot.h
/usr/include/libportal/session.h
/usr/include/libportal/settings.h
/usr/include/libportal/spawn.h
/usr/include/libportal/trash.h
/usr/include/libportal/types.h
/usr/include/libportal/updates.h
/usr/include/libportal/wallpaper.h
/usr/lib64/girepository-1.0/Xdp-1.0.typelib
/usr/lib64/girepository-1.0/XdpGtk3-1.0.typelib
/usr/lib64/libportal-gtk3.so
/usr/lib64/libportal-gtk3.so.1
/usr/lib64/libportal-gtk3.so.1.0.0
/usr/lib64/libportal.so
/usr/lib64/libportal.so.1
/usr/lib64/libportal.so.1.0.0
/usr/lib64/pkgconfig/libportal-gtk3.pc
/usr/lib64/pkgconfig/libportal.pc
/usr/share/gir-1.0/Xdp-1.0.gir
/usr/share/gir-1.0/XdpGtk3-1.0.gir

%changelog
* Tue Nov 03 2026 browneye <build@browneye.invalid> 0.9.1-1
- Sync with BLFS r13.1

* Tue Jan 19 2021 Chris Statzer <chris.statzer@qq.com> 0.3
- Initial RPM

