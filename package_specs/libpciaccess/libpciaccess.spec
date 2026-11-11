Name:       libpciaccess
Version:    0.19
Release:    1
Summary:    X.org PCI access library
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libpciaccess
Prefix:     /usr
Source0:    libpciaccess-0.19.tar.xz

%description
libpciaccess provides a portable interface to PCI devices.

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

%files -f %{_sourcedir}/libpciaccess.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.19-1
- Initial package
