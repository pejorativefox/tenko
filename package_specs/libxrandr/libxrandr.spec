Name:       libxrandr
Version:    1.5.5
Release:    2
Summary:    Xlib Resize, Rotate and Reflection (RandR) extension library.
License:    GPL3
Prefix:     /usr
Source0:    libXrandr-%{version}.tar.xz
%description
Xlib Resize, Rotate and Reflection (RandR) extension library.

%package devel
Summary:    libxrandr development files
Requires:   libxrandr = %{version}-%{release}

%description devel
Development files for libxrandr.

%package static
Summary:    libxrandr static libraries
Requires:   libxrandr = %{version}-%{release}

%description static
Static libraries for libxrandr.

%prep
%setup -q -n libXrandr-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxrandr.filelist
%files devel -f %{_sourcedir}/libxrandr-devel.filelist
%files static -f %{_sourcedir}/libxrandr-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.5.5-2
- Split devel, static payload into libxrandr-devel, libxrandr-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.5.5
- Sync with BLFS r13.1 (1.5.3)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.5.3-1
- Version bump
