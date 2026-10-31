Name:       desktop-file-utils
Version:    0.28
Release:    1
Summary:    Utilities for working with desktop entries
License:    GPL2
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
Utilities for validating and updating desktop entries and the MIME database.

%prep
%setup -q

%build
rm -fv /usr/bin/desktop-file-edit
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
* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.28
- Initial package (BLFS r13.1)
