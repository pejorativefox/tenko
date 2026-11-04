Name:       libxau
Version:    1.0.12
Release:    1
Summary:    X11 authorisation library
License:    GPL3
Source0:    libXau-%{version}.tar.xz
Prefix:     /usr

%description
X11 authorisation library

%prep
%setup -q -n libXau-%{version}

%build 
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxau.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.0.12
- Sync with BLFS r13.1 (1.0.11)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.0.11-1
- Version bump
