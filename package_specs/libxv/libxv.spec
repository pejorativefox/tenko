Name:       libxv
Version:    1.0.13
Release:    1
Summary:    Xlib-based library for the Xv extension
License:    MIT
Prefix:     /usr
Source0:    libXv-1.0.13.tar.xz

%description
Xlib-based library for the X Video (Xv) extension

%prep
%setup -q -n libXv-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxv.filelist
%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.0.13
- Sync with BLFS r13.1 (libxv 1.0.13)
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.0.12-1
- Version bump
