Name:       iso-codes
Version:    4.20.1
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    iso-codes-v4.20.1.tar.gz

%description
TODO

%prep
%setup -q -n iso-codes-v%{version}

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
* Sat Oct 31 2026 browneye <build@browneye.invalid> 4.20.1
- Sync with BLFS r13.1 (4.3)

# let's skip this for now

