Name:       libxslt
Version:    1.1.45
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    libxslt-1.1.45.tar.xz


%description
TODO

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

%changelog
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.33-1
- Version bump

