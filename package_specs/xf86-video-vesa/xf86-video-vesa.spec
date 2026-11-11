Name:       xf86-video-vesa
Version:    2.3.3
Release:    1
Summary:    Xorg generic VESA video driver
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/driver/xf86-video-vesa
Prefix:     /usr
Source0:    xf86-video-vesa-2.3.3.tar.bz2

%description
The generic VESA video driver for Xorg.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xf86-video-vesa.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 2.3.3-1
- Initial package
