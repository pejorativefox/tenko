Name:       libxcb
Version:    1.17.0
Release:    2
Summary:    X11 client library
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
X11 client library

%package devel
Summary:    libxcb development files
Requires:   libxcb = %{version}-%{release}

%description devel
Development files for libxcb.

%package doc
Summary:    libxcb documentation
Requires:   libxcb = %{version}-%{release}

%description doc
Documentation for libxcb.

%package static
Summary:    libxcb static libraries
Requires:   libxcb = %{version}-%{release}

%description static
Static libraries for libxcb.

%prep
%setup -q

%build 
%configure --without-doxygen
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxcb.filelist
%files devel -f %{_sourcedir}/libxcb-devel.filelist
%files doc -f %{_sourcedir}/libxcb-doc.filelist
%files static -f %{_sourcedir}/libxcb-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.17.0-2
- Split devel, doc, static payload into libxcb-devel, libxcb-doc, libxcb-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.17.0
- Sync with BLFS r13.1 (1.15)

# let's skip this for now
