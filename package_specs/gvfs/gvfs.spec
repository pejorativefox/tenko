Name:       gvfs
Version:    1.62.0
Release:    1
Summary:    Userspace virtual filesystem for GIO
License:    LGPL-2.0-or-later AND GPL-3.0-only AND MPL-2.0 AND BSD-3-Clause-Sun
URL:        https://wiki.gnome.org/Projects/gvfs
Source0:    gvfs-1.62.0.tar.xz
Prefix:     /usr

BuildRequires: meson
BuildRequires: ninja
BuildRequires: pkgconf
BuildRequires: glib
BuildRequires: gsettings-desktop-schemas
BuildRequires: libsecret
BuildRequires: fuse3
BuildRequires: samba
BuildRequires: systemd
BuildRequires: dbus-daemon
BuildRequires: gettext

Requires:   glib
Requires:   gsettings-desktop-schemas
Requires:   dbus-daemon

%description
gvfs provides the GIO virtual filesystem backends used by GTK applications
such as Thunar.  This build includes the SMB/CIFS and FUSE pieces.

%package fuse
Summary:    FUSE support for gvfs
Requires:   gvfs = %{version}-%{release}
Requires:   fuse3 >= 3.0.0

%description fuse
This package exposes gvfs mounts under /run/user/<uid>/gvfs with
gvfsd-fuse, so applications that do not use GIO can access remote files.

%package smb
Summary:    SMB/CIFS support for gvfs
Requires:   gvfs = %{version}-%{release}
Requires:   samba

%description smb
This package provides the gvfs SMB/CIFS backend for browsing Windows and
Samba shares in GIO applications such as Thunar.

%package lang
Summary:    gvfs translations
Requires:   gvfs = %{version}-%{release}

%description lang
Translations for gvfs.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..                 \
    --prefix=/usr              \
    --buildtype=release        \
    -Dsmb=true                 \
    -Dfuse=true                \
    -Dkeyring=true             \
    -Dlogind=true              \
    -Dgcr=false                \
    -Dadmin=false              \
    -Dhttp=false               \
    -Ddnssd=false              \
    -Dgudev=false              \
    -Dudisks2=false            \
    -Dafc=false                \
    -Dgoa=false                \
    -Dbluray=false             \
    -Dlibusb=false             \
    -Dgcrypt=false             \
    -Darchive=false            \
    -Dcdda=false               \
    -Dgoogle=false             \
    -Donedrive=false           \
    -Dgphoto2=false            \
    -Dmtp=false                \
    -Dafp=false                \
    -Dnfs=false                \
    -Dsftp=true                \
    -Dwsdd=false               \
    -Dman=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%post
if [ -x /usr/bin/glib-compile-schemas ]; then
    /usr/bin/glib-compile-schemas /usr/share/glib-2.0/schemas || :
fi
if [ -x /usr/bin/gio-querymodules ]; then
    /usr/bin/gio-querymodules %{_libdir}/gio/modules || :
fi

%posttrans
if [ -x /usr/bin/glib-compile-schemas ]; then
    /usr/bin/glib-compile-schemas /usr/share/glib-2.0/schemas || :
fi
if [ -x /usr/bin/gio-querymodules ]; then
    /usr/bin/gio-querymodules %{_libdir}/gio/modules || :
fi

%postun
if [ -x /usr/bin/glib-compile-schemas ]; then
    /usr/bin/glib-compile-schemas /usr/share/glib-2.0/schemas || :
fi
if [ -x /usr/bin/gio-querymodules ]; then
    /usr/bin/gio-querymodules %{_libdir}/gio/modules || :
fi

%files -f %{_sourcedir}/gvfs.filelist

%files fuse -f %{_sourcedir}/gvfs-fuse.filelist

%files smb -f %{_sourcedir}/gvfs-smb.filelist

%files lang -f %{_sourcedir}/gvfs-lang.filelist

%changelog
* Sat Nov 07 2026 tenko <build@tenko.invalid> 1.62.0-1
- New package: gvfs 1.62.0 (latest stable upstream) with the SMB and FUSE
  backends used by Thunar.
- Split gvfs-fuse, gvfs-smb and gvfs-lang.  Optional backends whose
  dependencies are not packaged (udisks2, Avahi, gcr-4, libsoup, libnfs,
  gphoto2, MTP, AFC, GOA, wsdd, libgcrypt) stay disabled.
- Compile GSettings schemas and the GIO module cache in %post,
  %posttrans and %postun so org.gnome.system.smb is available to Thunar.
