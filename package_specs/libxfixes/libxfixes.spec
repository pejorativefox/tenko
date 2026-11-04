Name:       libxfixes
Version:    6.0.2
Release:    2
Summary:    Xlib-based library for the XFIXES Extension.
License:    GPL3
Prefix:     /usr
Source0:    libXfixes-%{version}.tar.xz
%description
Xlib-based library for the XFIXES Extension.

%package devel
Summary:    libxfixes development files
Requires:   libxfixes = %{version}-%{release}

%description devel
Development files for libxfixes.

%package static
Summary:    libxfixes static libraries
Requires:   libxfixes = %{version}-%{release}

%description static
Static libraries for libxfixes.

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
%files devel -f %{_sourcedir}/libxfixes-devel.filelist
%files static -f %{_sourcedir}/libxfixes-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 6.0.2-2
- Split devel, static payload into libxfixes-devel, libxfixes-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 6.0.2
- Sync with BLFS r13.1 (6.0.1)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 6.0.1-1
- Version bump
