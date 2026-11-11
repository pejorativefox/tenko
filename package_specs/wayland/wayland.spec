Name:       wayland
Version:    1.26.0
Release:    3
Summary:    Wayland protocol libraries and reference compositor
License:    MIT
URL:        https://wayland.freedesktop.org/
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Wayland is a protocol for a compositor to talk to its clients, together with
a C library implementation of that protocol.  AppStream's display-detection
backend needs the wayland-client headers at build time.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup ..            \
      --prefix=/usr       \
      --buildtype=release \
      -Ddocumentation=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/wayland.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.26.0-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.26.0-1
- New package, synced with the base set.  Required by AppStream's
  display-detection backend.
