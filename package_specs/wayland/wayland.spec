Name:       wayland
Version:    1.26.0
Release:    3
Summary:    Wayland protocol libraries and reference compositor
License:    MIT
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
Wayland is a protocol for a compositor to talk to its clients, together with
a C library implementation of that protocol.  AppStream's display-detection
backend needs the wayland-client headers at build time.

%package devel
Summary:    Development files for wayland
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in wayland; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

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
%files devel

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.26.0-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.26.0-1
- New package, synced with BLFS r13.1.  Required by AppStream's
  display-detection backend.
