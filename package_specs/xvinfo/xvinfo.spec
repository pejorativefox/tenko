Name:       xvinfo
Version:    1.1.6
Release:    1
Summary:    Query the X11 Video extension (Xv)
License:    MIT
Prefix:     /usr
Source0:    xvinfo-1.1.6.tar.xz



%description
Query the X11 Video extension (Xv).

xvinfo is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xvinfo.filelist
%changelog
# let's skip this for now

