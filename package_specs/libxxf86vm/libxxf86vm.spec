Name:       libxxf86vm
Version:    1.1.7
Release:    1
Summary:    XFree86-VidMode X extension
License:    GPL3
Prefix:     /usr
Source0:    libXxf86vm-%{version}.tar.xz
%description
XFree86-VidMode X extension

%prep
%setup -q -n libXxf86vm-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxxf86vm.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.1.7
- Sync with BLFS r13.1 (1.1.5)

# let's skip this for now
