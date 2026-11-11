Name:       xf86-video-fbdev
Version:    0.5.1
Release:    1
Summary:    Xorg framebuffer (fbdev) video driver
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/driver/xf86-video-fbdev
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
The framebuffer (fbdev) video driver for Xorg.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xf86-video-fbdev.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 0.5.1-1
- Update to 0.5.1 (latest upstream release)
- Not in the base set; only the archive copy exists there, and it
  still lists 0.5.0, so the version was taken from upstream x.org
- Fix man page path in %files (/usr/share/man, not /usr/man)
