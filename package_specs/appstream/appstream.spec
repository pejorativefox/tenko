Name:       appstream
Version:    1.2.2
Release:    3
Summary:    Library and tool for software metadata
License:    LGPL
Source0:    AppStream-%{version}.tar.xz
Prefix:     /usr

%description
AppStream provides a library and tool for retrieving software metadata.
Flatpak requires libappstream for application metadata and catalogue
handling.

%package devel
Summary:    Development files for appstream
Requires:   %{name} = %{version}-%{release}

%description devel
The development files are back in appstream; this empty package only
exists so upgrades from the split layout resolve without a file
conflict.

%prep
%setup -q -n AppStream-%{version}

%build
mkdir build
pushd build
meson setup ..              \
      --prefix=/usr         \
      --buildtype=release   \
      -Dapidocs=false       \
      -Dbash-completion=false \
      -Dstemming=false      \
      -Dman=false
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/appstream.filelist
%files devel

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.2.2-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.2.2-1
- New package, synced with BLFS r13.1.  Flatpak 1.18 requires libappstream.
