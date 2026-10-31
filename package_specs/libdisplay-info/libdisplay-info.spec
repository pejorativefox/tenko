Name:       libdisplay-info
Version:    0.4.0
Release:    1
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

%files
/usr/

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.4.0
- Initial package (BLFS r13.1)
