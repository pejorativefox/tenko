Name:       libxdamage
Version:    1.1.7
Release:    2
Summary:    X Damage Extension library
License:    GPL3
Prefix:     /usr
Source0:    libXdamage-%{version}.tar.xz
%description
X Damage Extension library

%package devel
Summary:    libxdamage development files
Requires:   libxdamage = %{version}-%{release}

%description devel
Development files for libxdamage.

%package static
Summary:    libxdamage static libraries
Requires:   libxdamage = %{version}-%{release}

%description static
Static libraries for libxdamage.

%prep
%setup -q -n libXdamage-%{version}


%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxdamage.filelist
%files devel -f %{_sourcedir}/libxdamage-devel.filelist
%files static -f %{_sourcedir}/libxdamage-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.7-2
- Split devel, static payload into libxdamage-devel, libxdamage-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.1.7
- Sync with BLFS r13.1 (1.1.6)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.6-1
- Version bump
