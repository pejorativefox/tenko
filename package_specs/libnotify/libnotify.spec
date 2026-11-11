Name:       libnotify
Version:    0.8.9
Release:    3
Summary:    Desktop notification library
License:    LGPL-2.1-or-later
URL:        https://gitlab.gnome.org/GNOME/libnotify
Prefix:     /usr
Source0:    libnotify-0.8.9.tar.xz
BuildRequires: gdk-pixbuf
BuildRequires: shared-mime-info
BuildRequires: libjpeg-turbo
BuildRequires: libpng
BuildRequires: gobject-introspection

%description
libnotify is a library for sending desktop notifications to a notification
daemon, as defined in the freedesktop.org Desktop Notifications
specification. It also provides a wrapper for the XDG Portal Notification
API.

%prep
%setup -a 0

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release -D gtk_doc=false -D man=false -D tests=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%package gir
Summary:    GObject Introspection data for libnotify
License:    LGPL-2.1-or-later
Requires:   %{name} = %{version}-%{release}

%description gir
GObject Introspection typelibs for libnotify, split out of the runtime
package so a plain install does not carry the introspection data.
The .gir XML needed for building stays in the main package.

%files -f %{_sourcedir}/libnotify.filelist
%files gir -f %{_sourcedir}/libnotify-gir.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.8.9-3
- Replace the TODO summary/description and record the verified license
  (LGPL-2.1-or-later): COPYING (issue #8).

* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.8.9-2
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 0.8.9-1
- Update to 0.8.9 (current upstream, D9 parity)
- Split the GObject Introspection typelibs into %{name}-gir; the -devel package now requires it
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.8.8-2
- Split devel payload into libnotify-devel (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.8.8
- Sync with 0.7.8

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.7.8-1
- Version bump

