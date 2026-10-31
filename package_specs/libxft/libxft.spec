Name:       libxft
Version:    2.3.9
Release:    1
Summary:    Xorg font rendering library
License:    GPL3
Prefix:     /usr
Source0:    libXft-%{version}.tar.xz
%description
Client side font rendering library, using libfreetype, libX11, and the X Render extension to display anti-aliased text.

%prep
%setup -q -n libXft-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxft.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 2.3.9
- Sync with BLFS r13.1 (2.3.8)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 2.3.8-1
- Version bump
