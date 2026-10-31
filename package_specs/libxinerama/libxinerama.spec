Name:       libxinerama
Version:    1.1.6
Release:    1
Summary:    Xlib API for Xinerama extension to X11 Protocol
License:    GPL3
Prefix:     /usr
Source0:    libXinerama-%{version}.tar.xz
%description
Xlib API for Xinerama extension to X11 Protocol

%prep
%setup -q -n libXinerama-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxinerama.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.1.6
- Sync with BLFS r13.1 (1.1.5)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.5-1
- Version bump
