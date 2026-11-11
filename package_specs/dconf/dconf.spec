Name:       dconf
Version:    51.0
Release:    2
Summary:    Dconf backend for gsettings
License:    LGPL-2.1-or-later
Prefix:     /usr
URL:        https://download.gnome.org/sources/dconf/
Source0:    %{name}-%{version}.tar.xz
BuildRequires: bash-completion
BuildRequires: dbus-daemon

%description
Dconf is a low-level configuration system and settings management
framework.  It provides the backend for GSettings.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -Dgtk_doc=false     \
      -Dman=false         \
      -Dvapi=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/dconf.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 51.0-2
- Package the upstream dconf bash completion instead of forcing
  -Dbash_completion=false.  The base build image now provides
  bash-completion.pc.

* Thu Nov 05 2026 browneye <build@browneye.invalid> 51.0-1
- Update to 51.0.
- Build only dconf itself; dconf-editor is a separate package and is
  not built here.
- Disable gtk-doc, man pages and vala bindings that the base image
  cannot build.
