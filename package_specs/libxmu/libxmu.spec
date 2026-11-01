Name:       libxmu
Version:    1.3.1
Release:    2
Summary:    Xlib misc utilities
License:    GPL3
Prefix:     /usr
Source0:    libXmu-%{version}.tar.xz

BuildRequires: libxt

%description
This library contains miscellaneous utilities and is not part of the Xlib standard. 

%package devel
Summary:    libxmu development files
Requires:   libxmu = %{version}-%{release}

%description devel
Development files for libxmu.

%package doc
Summary:    libxmu documentation
Requires:   libxmu = %{version}-%{release}

%description doc
Documentation for libxmu.

%package static
Summary:    libxmu static libraries
Requires:   libxmu = %{version}-%{release}

%description static
Static libraries for libxmu.

%prep
%setup -q -n libXmu-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxmu.filelist
%files devel -f %{_sourcedir}/libxmu-devel.filelist
%files doc -f %{_sourcedir}/libxmu-doc.filelist
%files static -f %{_sourcedir}/libxmu-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.3.1-2
- Split devel, doc, static payload into libxmu-devel, libxmu-doc, libxmu-static (size audit)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.4-1
- Version bump
