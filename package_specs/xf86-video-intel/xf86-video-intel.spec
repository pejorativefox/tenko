Name:       xf86-video-intel
Version:    20230223
Release:    1
Summary:    Xorg Intel video driver
License:    MIT
Prefix:     /usr
Source0:    xf86-video-intel-20230223.tar.xz

%description
The Intel video driver for Xorg.

%prep
%setup -q

%build
%configure --enable-kms-only --enable-uxa
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/

%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 20230223-1
- Initial package (BLFS r13.1)
