Name:       xf86-input-libinput
Version:    1.5.0
Release:    1
Summary:    Xorg libinput input driver
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/driver/xf86-input-libinput
Prefix:     /usr
Source0:    xf86-input-libinput-1.5.0.tar.xz

%description
The Xorg driver that feeds libinput events into the X server.

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

%files -f %{_sourcedir}/xf86-input-libinput.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.5.0-1
- Initial package
