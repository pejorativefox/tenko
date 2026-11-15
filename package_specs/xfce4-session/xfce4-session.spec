Name:       xfce4-session
Version:    4.20.4
Release:    5
Summary:    A session manager for Xfce
License:    GPL-2.0-or-later AND GPL-2.0-only
URL:        https://docs.xfce.org/xfce/xfce4-session/start
Source0:    %{name}-%{version}.tar.bz2
Prefix:     /usr

BuildRequires: iceauth
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: harfbuzz
BuildRequires: libice
BuildRequires: libsm
BuildRequires: libx11
BuildRequires: libxfce4ui
BuildRequires: libxfce4util
BuildRequires: libxfce4windowing
BuildRequires: pango
BuildRequires: polkit
BuildRequires: xfconf

%description
A session manager for Xfce

%package lang
Summary:    xfce4-session translations
Requires:   xfce4-session = %{version}-%{release}

%description lang
Translations for xfce4-session.

%prep
%setup

%build
%configure --disable-legacy-sm
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
# The upstream file names xapp first for Wallpaper, Screenshot, Background
# and Settings, but xapp is not packaged and the X11 session cannot use the
# wlr Screenshot/ScreenCast backends.  Select the GTK backend by default so
# the interfaces it implements (FileChooser, AppChooser, Print,
# Notification, Inhibit, Access, Account, Email, DynamicLauncher, Lockdown,
# Settings) resolve without a missing-backend warning (issue #41).
cat > %{buildroot}%{_datadir}/xdg-desktop-portal/xfce-portals.conf <<'EOF'
[preferred]
default=gtk;
org.freedesktop.impl.portal.Secret=gnome-keyring;
EOF

%files -f %{_sourcedir}/xfce4-session.filelist
%files lang -f %{_sourcedir}/xfce4-session-lang.filelist


%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20.4-5
- Select the gnome-keyring backend for the portal Secret interface now that
  issue #39 ships the provider (issue #39, #41).

* Sun Nov 08 2026 tenko <build@tenko.invalid> 4.20.4-4
- Replace xfce-portals.conf with a `default=gtk` selection.  The upstream
  file names xapp for Wallpaper, Screenshot, Background and Settings (not
  packaged) and wlr for ScreenCast (Wayland-only), so the X11 session
  produced missing-backend warnings.  The GTK backend implements
  FileChooser, AppChooser, Print, Notification, Inhibit, Access, Account,
  Email, DynamicLauncher, Lockdown and Settings; the remaining interfaces
  are documented as unsupported (issue #41).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 4.20.4-3
- Replace the legacy short licence name with the verified SPDX expression
  (GPL-2.0-or-later AND GPL-2.0-only): COPYING (issue #8).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 4.20.4-2
- Split lang payload into xfce4-session-lang (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.4
- Sync with 4.19.1

* Wed Aug 30 2023 Chris Statzer <chris.statzer@gmail.com> 4.19.1
- Version bump

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 4.14.0
- Initial RPM

