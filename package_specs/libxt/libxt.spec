Name:       libxt
Version:    1.3.1
Release:    2
Summary:    X Toolkit Intrinsics library
License:    GPL3
Prefix:     /usr
Source0:    libXt-%{version}.tar.xz

BuildRequires: libsm

%description
X Toolkit Intrinsics library

%package devel
Summary:    libxt development files
Requires:   libxt = %{version}-%{release}

%description devel
Development files for libxt.

%package doc
Summary:    libxt documentation
Requires:   libxt = %{version}-%{release}

%description doc
Documentation for libxt.

%package static
Summary:    libxt static libraries
Requires:   libxt = %{version}-%{release}

%description static
Static libraries for libxt.

%prep
%setup -q -n libXt-%{version}


%build
%configure --with-appdefaultdir=/etc/X11/app-defaults
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxt.filelist
%files devel -f %{_sourcedir}/libxt-devel.filelist
%files doc -f %{_sourcedir}/libxt-doc.filelist
%files static -f %{_sourcedir}/libxt-static.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.3.1-2
- Split devel, doc, static payload into libxt-devel, libxt-doc, libxt-static (size audit)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.3.0-1
- Version bump
