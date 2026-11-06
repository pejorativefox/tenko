Name:       appstream
Version:    1.2.2
Release:    4
Summary:    Library and tool for software metadata
License:    LGPL-2.1-or-later AND FSFAP
Source0:    AppStream-%{version}.tar.xz
Prefix:     /usr

%description
AppStream provides a library and tool for retrieving software metadata.
Flatpak requires libappstream for application metadata and catalogue
handling.

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

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.2-4
- Replace the legacy short licence name with the verified SPDX expression
  (LGPL-2.1-or-later AND FSFAP): COPYING, data/update-data.py and data/its/metainfo.its (issue #8).

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.2.2-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Wed Nov 04 2026 browneye <build@browneye.invalid> 1.2.2-1
- New package, synced with the base set.  Flatpak 1.18 requires libappstream.
