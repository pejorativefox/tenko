Name:       libxscrnsaver
Version:    1.2.5
Release:    2
Summary:    X11 screensaver library
License:    X11
URL:        https://gitlab.freedesktop.org/xorg/lib/libxscrnsaver
Prefix:     /usr
Source0:    libXScrnSaver-%{version}.tar.xz
BuildRequires: libx11
BuildRequires: libxext
BuildRequires: util-macros
BuildRequires: xorgproto

%description
X11 screensaver library

%prep
%setup -q -n libXScrnSaver-%{version}


%build
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxscrnsaver.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.5-2
- Record the verified license (X11): COPYING (issue #8).

* Tue Nov 03 2026 browneye <build@browneye.invalid> 1.2.5-1
- Sync with the base set

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.4-1
- Version bump
