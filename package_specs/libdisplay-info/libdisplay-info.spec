Name:       libdisplay-info
Version:    0.4.0
Release:    3
Summary:    EDID and DisplayID library
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
libdisplay-info parses EDID and DisplayID metadata for displays.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files -f %{_sourcedir}/libdisplay-info.filelist

%changelog
* Wed Nov 04 2026 browneye <build@browneye.invalid> 0.4.0-3
- Revert the -devel split (issue #4): the headers, include
  directories, unversioned .so symlinks and pkg-config files return
  to the runtime package.
  The now-empty -devel package is kept so an upgrade from the
  split layout resolves without a file conflict.

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.4.0
- Initial package
