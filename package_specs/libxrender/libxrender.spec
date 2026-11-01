Name:       libxrender
Version:    0.9.12
Release:    2
Summary:    Render Extension to the X11 protocol.
License:    GPL3
Prefix:     /usr
Source0:    libXrender-%{version}.tar.xz
%description
Render Extension to the X11 protocol.

%package devel
Summary:    libxrender development files
Requires:   libxrender = %{version}-%{release}

%description devel
Development files for libxrender.

%package static
Summary:    libxrender static libraries
Requires:   libxrender = %{version}-%{release}

%description static
Static libraries for libxrender.

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
%files devel -f %{_sourcedir}/libxrender-devel.filelist
%files static -f %{_sourcedir}/libxrender-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 0.9.12-2
- Split devel, static payload into libxrender-devel, libxrender-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 0.9.12
- Sync with BLFS r13.1 (0.9.11)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.9.11-1
- Version bump
