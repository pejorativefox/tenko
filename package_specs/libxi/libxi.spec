Name:       libxi
Version:    1.8.4
Release:    1
Summary:    Library for the X Input Extension.
License:    GPL3
Prefix:     /usr
Source0:    libXi-%{version}.tar.xz
%description
Library for the X Input Extension.

%package devel
Summary:    libxi development files
Requires:   libxi = %{version}-%{release}

%description devel
Development files for libxi.

%package doc
Summary:    libxi documentation
Requires:   libxi = %{version}-%{release}

%description doc
Documentation for libxi.

%package static
Summary:    libxi static libraries
Requires:   libxi = %{version}-%{release}

%description static
Static libraries for libxi.

%prep
%setup -q -n libXi-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxi.filelist
%files devel -f %{_sourcedir}/libxi-devel.filelist
%files doc -f %{_sourcedir}/libxi-doc.filelist
%files static -f %{_sourcedir}/libxi-static.filelist


%changelog
* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.8.4-1
- Update to 1.8.4 (current BLFS r13.1 trunk version).

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.8.3-2
- Split devel, doc, static payload into libxi-devel, libxi-doc, libxi-static (size audit)

* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.8.3
- Sync with BLFS r13.1 (1.8.1)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.8.1-1
- Version bump
