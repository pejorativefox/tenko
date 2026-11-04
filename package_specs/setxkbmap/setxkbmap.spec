Name:       setxkbmap
Version:    1.3.5
Release:    1
Summary:    Set the X11 keyboard layout
License:    MIT
Prefix:     /usr
Source0:    setxkbmap-1.3.5.tar.xz



%description
Set the X11 keyboard layout.

setxkbmap is maintained at its BLFS r13.1 version and is built
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

%files -f %{_sourcedir}/setxkbmap.filelist
%changelog
# let's skip this for now

