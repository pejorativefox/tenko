Name:       xdg-user-dirs
Version:    0.20
Release:    1
Summary:    Manage user directories like ~/Desktop and ~/Music
License:    GPL-2.0-or-later
URL:        https://gitlab.freedesktop.org/xdg/xdg-user-dirs
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

BuildRequires: meson
BuildRequires: ninja
BuildRequires: gcc
BuildRequires: gettext
BuildRequires: systemd

%description
xdg-user-dirs is a tool to help manage "well known" user directories like
the desktop folder, music folder, documents folder, and so on.  It also
handles localization for the standard user directories.

The package installs the upstream autostart entry and systemd user unit, so
xdg-user-dirs-update runs in a new graphical session and creates
~/.config/user-dirs.dirs without moving or overwriting user files.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..              \
      --prefix=/usr         \
      --buildtype=release   \
      -Ddocs=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/xdg-user-dirs.filelist

%changelog
* Sun Nov 08 2026 tenko <build@tenko.invalid> 0.20-1
- Initial package (xdg-user-dirs 0.20, latest stable upstream release,
  tagged 2026-04-08).  Ship the upstream autostart entry and systemd user
  unit so xdg-user-dirs-update creates ~/.config/user-dirs.dirs and the
  standard user directories at first session start without touching
  existing files.  Man pages are not built because the base build image
  has no xsltproc or DocBook stylesheet, and upstream generates them at
  build time rather than shipping them in the tarball (issue #34).
