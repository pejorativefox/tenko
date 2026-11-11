Name:       libxvmc
Version:    1.0.15
Release:    2
Summary:    Xlib-based X-Video Motion Compensation API.
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/lib/libxvmc
Prefix:     /usr
Source0:    libXvMC-%{version}.tar.xz

BuildRequires: libxv

%description
Xlib-based X-Video Motion Compensation API.

%prep
%setup -q -n libXvMC-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxvmc.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.15-2
- Record the verified license (MIT): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.0.15-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.0.13-1
- Version bump
