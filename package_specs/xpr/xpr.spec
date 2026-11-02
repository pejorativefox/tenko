Name:       xpr
Version:    1.2.1
Release:    1
Summary:    Print X11 window dumps
License:    MIT
Prefix:     /usr
Source0:    xpr-1.2.1.tar.xz



%description
Print X11 window dumps.

xpr is maintained at its BLFS r13.1 version and is built
with the standard autotools build inline in its spec.


%prep
%setup -q

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xpr.filelist
%changelog
# let's skip this for now

