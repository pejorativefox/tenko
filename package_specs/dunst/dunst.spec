Name:       dunst
Version:    1.13.2
Release:    1
Summary:    Lightweight notification daemon for Linux
License:    BSD-3-Clause
Prefix:     /usr
URL:        https://dunst-project.org/
Source0:    %{name}-%{version}.tar.gz

%description
Dunst is a lightweight replacement for the notification daemons
provided by most desktop environments.  It is highly configurable and
works with any X11 or Wayland desktop.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..              \
      --prefix=/usr         \
      --buildtype=release   \
      -Dwayland=disabled    \
      -Dsystemd=disabled    \
      -Ddunstify=disabled
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/dunst.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.13.2-1
- Update to 1.13.2; not in the r13.1 book, latest upstream stable
  2026-11-05 (tag v1.13.2, released 2026-03-18).
- Build from the upstream GitHub archive because the release page has
  no source asset attached; the extracted top directory is dunst-1.13.2.
- Disable Wayland support (no Wayland client libraries in the base
  image), systemd user units and the libnotify-based dunstify utility.
  X11 support and the man pages stay enabled.
- dunst no longer depends on libxdg-basedir; that dependency was
  removed upstream before 1.13.2.
