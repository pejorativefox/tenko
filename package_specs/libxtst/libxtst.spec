Name:       libxtst
Version:    1.2.5
Release:    2
Summary:    Xlib-based library for XTEST & RECORD
License:    GPL3
Prefix:     /usr
Source0:    libXtst-%{version}.tar.xz

BuildRequires: libxi

%description
Xlib-based library for XTEST & RECORD

%package devel
Summary:    libxtst development files
Requires:   libxtst = %{version}-%{release}

%description devel
Development files for libxtst.

%package static
Summary:    libxtst static libraries
Requires:   libxtst = %{version}-%{release}

%description static
Static libraries for libxtst.

%prep
%setup -q -n libXtst-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxtst.filelist
%files devel -f %{_sourcedir}/libxtst-devel.filelist
%files static -f %{_sourcedir}/libxtst-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.2.5-2
- Split devel, static payload into libxtst-devel, libxtst-static (size audit)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.2.4-1
- Version bump
