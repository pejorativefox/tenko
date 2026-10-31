Name:       libxfixes
Version:    6.0.2
Release:    1
Summary:    Xlib-based library for the XFIXES Extension.
License:    GPL3
Prefix:     /usr
Source0:    libXfixes-%{version}.tar.xz
%description
Xlib-based library for the XFIXES Extension.

%prep
%setup -q -n libXfixes-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxfixes.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 6.0.2
- Sync with BLFS r13.1 (6.0.1)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 6.0.1-1
- Version bump
