Name:       libevdev
Version:    1.13.6
Release:    1
Summary:    Wrapper library for evdev devices
License:    MIT
Prefix:     /usr
Source0:    libevdev-1.13.6.tar.xz

%description
libevdev wraps the Linux evdev interface for input device handling.

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

%files -f %{_sourcedir}/libevdev.filelist

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.13.6-1
- Initial package (BLFS r13.1)
