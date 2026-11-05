Name:       xf86-video-vmware
Version:    13.4.0
Release:    1
Summary:    Xorg VMware video driver
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

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
- Keep 13.4.0: latest upstream release, and the same version the archived
  BLFS page lists (the package is not in the r13.1 book outside archive/)
- Fix man page path in %files (/usr/share/man, not /usr/man)
