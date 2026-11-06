Name:       xgamma
Version:    1.0.8
Release:    1
Summary:    Set the X11 gamma correction
License:    MIT
Prefix:     /usr
Source0:    xgamma-1.0.8.tar.xz



%description
Set the X11 gamma correction.

xgamma is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xgamma.filelist
%changelog
# let's skip this for now

