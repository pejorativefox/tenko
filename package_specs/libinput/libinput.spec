Name:       libinput
Version:    1.32.0
Release:    1
Summary:    Input device library
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
libinput is the input device handling library used by Xorg and Wayland compositors.

%prep
%setup -q

%build
mkdir build
pushd build
meson setup .. --prefix=/usr --buildtype=release -Ddebug-gui=false -Dtests=false -Dlibwacom=false -Dudev-dir=/usr/lib/udev
ninja
popd

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
pushd build
DESTDIR=%{buildroot} ninja install
popd
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libinput.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.31.3-1
- Initial package
