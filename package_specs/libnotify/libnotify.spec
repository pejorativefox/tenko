Name:       libnotify
Version:    0.8.8
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    libnotify-0.8.8.tar.xz

%description
TODO

%prep
%setup -a 0

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release -D gtk_doc=false -D man=false -D tests=false
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
* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.8.8
- Sync with BLFS r13.1 (0.7.8)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.7.8-1
- Version bump

