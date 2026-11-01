Name:       libxext
Version:    1.3.7
Release:    2
Summary:    Library for common extensions to the X11 protocol
License:    GPL3
Prefix:     /usr
Source0:    libXext-%{version}.tar.xz
%description
Library for common extensions to the X11 protocol

%package devel
Summary:    libxext development files
Requires:   libxext = %{version}-%{release}

%description devel
Development files for libxext.

%package static
Summary:    libxext static libraries
Requires:   libxext = %{version}-%{release}

%description static
Static libraries for libxext.

%prep
%setup -q -n libXext-%{version}


%build
%configure ICE_LIBS=-lpthread
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxext.filelist
%files devel -f %{_sourcedir}/libxext-devel.filelist
%files static -f %{_sourcedir}/libxext-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.3.7-2
- Split devel, static payload into libxext-devel, libxext-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.3.7
- Sync with BLFS r13.1 (1.3.5)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.3.5-1
- Version bump
