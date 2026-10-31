Name:       libxrender
Version:    0.9.12
Release:    1
Summary:    Render Extension to the X11 protocol.
License:    GPL3
Prefix:     /usr
Source0:    libXrender-%{version}.tar.xz
%description
Render Extension to the X11 protocol.

%prep
%setup -q -n libXrender-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxrender.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.9.12
- Sync with BLFS r13.1 (0.9.11)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.9.11-1
- Version bump
