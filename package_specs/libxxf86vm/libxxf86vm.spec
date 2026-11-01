Name:       libxxf86vm
Version:    1.1.7
Release:    2
Summary:    XFree86-VidMode X extension
License:    GPL3
Prefix:     /usr
Source0:    libXxf86vm-%{version}.tar.xz
%description
XFree86-VidMode X extension

%package devel
Summary:    libxxf86vm development files
Requires:   libxxf86vm = %{version}-%{release}

%description devel
Development files for libxxf86vm.

%package static
Summary:    libxxf86vm static libraries
Requires:   libxxf86vm = %{version}-%{release}

%description static
Static libraries for libxxf86vm.

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
%files devel -f %{_sourcedir}/libxxf86vm-devel.filelist
%files static -f %{_sourcedir}/libxxf86vm-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.7-2
- Split devel, static payload into libxxf86vm-devel, libxxf86vm-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.1.7
- Sync with BLFS r13.1 (1.1.5)

# let's skip this for now
