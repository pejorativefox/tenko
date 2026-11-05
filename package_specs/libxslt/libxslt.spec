Name:       libxslt
Version:    1.1.45
Release:    4
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
%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.1.45-4
- Remove the -devel subpackage: fold its headers, include
  directories, unversioned .so symlinks and .pc files into the
  main package (issue #4).

* Mon Nov 02 2026 browneye <build@browneye.invalid> 1.1.45-3
- Rebuild for Python 3.15 (3.14 site-packages are gone); 0 paths updated.

* Sun Nov 01 2026 browneye <build@browneye.invalid> 1.1.45-2
- Split doc, devel payload into libxslt-doc, libxslt-devel (size audit)

* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.33-1
- Version bump

