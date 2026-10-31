Name:       upower
Version:    1.91.3
Release:    1
Summary:    Abstraction for enumerating power devices, listening to device events and querying history and statistics
License:    GPL
Source0:    upower-v1.91.3.tar.bz2
Prefix:     /usr

BuildRequires: libgudev
BuildRequires: libusb
BuildRequires: udev

%description
Abstraction for enumerating power devices, listening to device events and querying history and statistics

%prep
%setup -q -n upower-v%{version}

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release -D gtk-doc=false -D man=false -D systemdsystemunitdir=no -D udevrulesdir=/usr/lib/udev/rules.d
ninja
popd

%install
rm -rf %{buildroot}
pushd build
DESTDIR=%{buildroot} ninja install
popd

%files
/usr/
/etc/

%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.91.3
- Sync with BLFS r13.1 (0.99.7)

* Tue Dec 10 2019 Chris Statzer <chris.statzer@qq.com> 0.99.7
- Initial RPM

