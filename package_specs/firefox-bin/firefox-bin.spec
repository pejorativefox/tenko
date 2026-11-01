Name:       firefox-bin
Version:    159.0
Release:    1
Summary:    Mozilla Firefox web browser (official upstream linux-x86_64 build)
License:    MPL-2.0
URL:        https://www.mozilla.org/firefox/
Prefix:     /opt
Source0:    firefox-%{version}.tar.xz
Source1:    firefox.desktop

# Prebuilt binaries: do not let rpm guess dependencies from /opt, the
# explicit list below is what libxul.so actually links against.
AutoProv: no
AutoReq: no

Provides:   firefox = %{version}-%{release}
Provides:   web_browser

Requires:   ld-linux-x86-64.so.2()(64bit)
Requires:   libc.so.6()(64bit)
Requires:   libm.so.6()(64bit)
Requires:   libdl.so.2()(64bit)
Requires:   libpthread.so.0()(64bit)
Requires:   librt.so.1()(64bit)
Requires:   libstdc++.so.6()(64bit)
Requires:   libgcc_s.so.1()(64bit)
Requires:   libX11.so.6()(64bit)
Requires:   libX11-xcb.so.1()(64bit)
Requires:   libXcomposite.so.1()(64bit)
Requires:   libXdamage.so.1()(64bit)
Requires:   libXext.so.6()(64bit)
Requires:   libXfixes.so.3()(64bit)
Requires:   libXrandr.so.2()(64bit)
Requires:   libXrender.so.1()(64bit)
Requires:   libXcursor.so.1()(64bit)
Requires:   libXi.so.6()(64bit)
Requires:   libxcb.so.1()(64bit)
Requires:   libxcb-shm.so.0()(64bit)
Requires:   libasound.so.2()(64bit)
Requires:   libgtk-3.so.0()(64bit)
Requires:   libgdk-3.so.0()(64bit)
Requires:   libglib-2.0.so.0()(64bit)
Requires:   libgobject-2.0.so.0()(64bit)
Requires:   libgio-2.0.so.0()(64bit)
Requires:   libpango-1.0.so.0()(64bit)
Requires:   libpangocairo-1.0.so.0()(64bit)
Requires:   libatk-1.0.so.0()(64bit)
Requires:   libcairo.so.2()(64bit)
Requires:   libcairo-gobject.so.2()(64bit)
Requires:   libgdk_pixbuf-2.0.so.0()(64bit)
Requires:   libfreetype.so.6()(64bit)
Requires:   libfontconfig.so.1()(64bit)
Requires:   libdbus-1.so.3()(64bit)
Requires:   hicolor-icon-theme
Requires:   desktop-file-utils

%description
Mozilla Firefox is a standalone web browser built on the Gecko engine.

This package repackages the official Mozilla build for linux-x86_64
(release channel) under /opt/firefox, with a /usr/bin/firefox launcher,
the desktop entry and the hicolor icons.  It is a binary distribution, not
a build from source: use it when a full Rust/Clang source build is not
wanted.

%prep
rm -rf firefox
tar -xf %{SOURCE0}

%build
# Prebuilt payload: nothing to compile.

%install
rm -rf %{buildroot}
install -d %{buildroot}/opt
cp -a firefox %{buildroot}/opt/firefox

install -d %{buildroot}%{_bindir}
ln -s /opt/firefox/firefox %{buildroot}%{_bindir}/firefox

install -d %{buildroot}%{_datadir}/applications
install -m644 %{SOURCE1} %{buildroot}%{_datadir}/applications/firefox.desktop

for size in 16 32 48 64 128; do
    install -d %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps
    install -m644 firefox/browser/chrome/icons/default/default${size}.png \
        %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/firefox.png
done

%post
update-desktop-database %{_datadir}/applications &>/dev/null || :

%postun
update-desktop-database %{_datadir}/applications &>/dev/null || :

%files
%dir /opt/firefox
/opt/firefox/*
%{_bindir}/firefox
%{_datadir}/applications/firefox.desktop
%{_datadir}/icons/hicolor/*/apps/firefox.png

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 159.0-1
- Update to Firefox 159.0 (current release; the spec was at 116.0.3 from
  2023) using the official linux-x86_64 .tar.xz
- Fix the install layout: the desktop entry went to /share/applications
  instead of /usr/share/applications; add the hicolor icons, a
  /usr/bin/firefox launcher and desktop-database scriptlets
- Replace the placeholder Summary/description and declare the real
  libxul.so runtime dependencies, including libasound.so.2
