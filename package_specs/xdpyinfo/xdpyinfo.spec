Name:       xdpyinfo
Version:    1.4.0
Release:    1
Summary:    Display information about an X server
License:    MIT
Prefix:     /usr
Source0:    xdpyinfo-1.4.0.tar.xz



%description
Display information about an X server.

xdpyinfo is maintained at its BLFS r13.1 version and is built
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

%files -f %{_sourcedir}/xdpyinfo.filelist
%changelog
# let's skip this for now

