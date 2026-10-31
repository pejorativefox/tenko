Name:       xkeyboard-config
Version:    2.48
Release:    1
Summary:    X keyboard configuration data
License:    MIT
Prefix:     /usr
Source0:    xkeyboard-config-2.48.tar.xz

%description
xkeyboard-config provides the XKB keyboard description database.

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
mkdir -p %{buildroot}/etc
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xkeyboard-config.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.48-1
- Initial package (BLFS r13.1)
