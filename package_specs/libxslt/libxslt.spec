Name:       libxslt
Version:    1.1.45
Release:    2
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    libxslt-1.1.45.tar.xz


%description
TODO

%package doc
Summary:    libxslt documentation
Requires:   libxslt = %{version}-%{release}

%description doc
Documentation for libxslt.

%package devel
Summary:    libxslt development files
Requires:   libxslt = %{version}-%{release}

%description devel
Development files for libxslt.

%prep
%setup -a 0

%build
sed -i s/3000/5000/ libxslt/transform.c doc/xsltproc.{1,xml} 
%configure  --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxslt.filelist
%files doc -f %{_sourcedir}/libxslt-doc.filelist
%files devel -f %{_sourcedir}/libxslt-devel.filelist


%changelog
* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.45-2
- Split doc, devel payload into libxslt-doc, libxslt-devel (size audit)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.33-1
- Version bump

