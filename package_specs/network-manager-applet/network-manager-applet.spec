Name:       network-manager-applet
Version:    1.34.0
Release:    2
Summary:    NetworkManager GUI applet and connection editor
License:    GPL-2.0-or-later
URL:        https://gitlab.gnome.org/GNOME/network-manager-applet
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: NetworkManager
BuildRequires: at-spi2-core
BuildRequires: cairo
BuildRequires: gdk-pixbuf
BuildRequires: gtk+
BuildRequires: libnma
BuildRequires: libsecret
BuildRequires: pango

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

%files -f %{_sourcedir}/network-manager-applet.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.34.0-2
- Replace the TODO summary/description and record the verified license
  (GPL-2.0-or-later): src/main.c (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.34.0-1
- Sync with the base set

# let's skip this for now

