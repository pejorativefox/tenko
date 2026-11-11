Name:       xkeyboard-config
Version:    2.48
Release:    2
Summary:    X keyboard configuration data
License:    MIT
URL:        https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config
Prefix:     /usr
Source0:    xkeyboard-config-2.48.tar.xz

%description
xkeyboard-config provides the XKB keyboard description database.

%package lang
Summary:    xkeyboard-config translations
Requires:   xkeyboard-config = %{version}-%{release}

%description lang
Translations for xkeyboard-config.

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
%files lang -f %{_sourcedir}/xkeyboard-config-lang.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.48-2
- Split lang payload into xkeyboard-config-lang (size audit)

* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.48-1
- Initial package
