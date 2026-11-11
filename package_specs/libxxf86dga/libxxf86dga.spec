Name:       libxxf86dga
Version:    1.1.7
Release:    2
Summary:    Client library for the XFree86-DGA extension
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxxf86dga
Prefix:     /usr
Source0:    libXxf86dga-%{version}.tar.xz
BuildRequires: libx11
BuildRequires: libxext
BuildRequires: util-macros
BuildRequires: xorgproto

%description
Client library for the XFree86-DGA extension

%prep
%setup -q -n libXxf86dga-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxxf86dga.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.7-2
- Record the verified license (MIT): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.1.7-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.6-1
- Version bump
