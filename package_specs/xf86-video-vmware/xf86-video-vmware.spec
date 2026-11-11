Name:       xf86-video-vmware
Version:    13.4.0
Release:    1
Summary:    Xorg VMware video driver
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/driver/xf86-video-vmware
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz
BuildRequires: util-macros
BuildRequires: xorg-server
BuildRequires: xorgproto

%description
The VMware video driver for Xorg.

%prep
%setup -q

%build
%configure
%make_build

%install
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xf86-video-vmware.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 13.4.0-1
- Keep 13.4.0: latest upstream release, and the package is not part of the base set
- Fix man page path in %files (/usr/share/man, not /usr/man)
