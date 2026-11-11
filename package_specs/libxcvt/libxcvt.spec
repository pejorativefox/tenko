Name:       libxcvt
Version:    0.1.3
Release:    1
Summary:    VESA CVT modeline library
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxcvt
Prefix:     /usr
Source0:    libxcvt-0.1.3.tar.xz

%description
libxcvt provides the CVT modeline generation used by Xorg.

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

%files -f %{_sourcedir}/libxcvt.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.1.3-1
- Initial package
