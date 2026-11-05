Name:       dconf
Version:    51.0
Release:    1
Summary:    Dconf backend for gsettings
License:    LGPL2.1
Prefix:     /usr
URL:        https://download.gnome.org/sources/dconf/
Source0:    %{name}-%{version}.tar.xz

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
      -Dbash_completion=false \
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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 51.0-1
- Update to 51.0 (BLFS r13.1, gnome/platform/dconf.xml).
- Build only dconf itself; dconf-editor is a separate package and is
  not built here.
- Disable bash-completion, gtk-doc, man pages and vala bindings that
  the base image cannot build.
