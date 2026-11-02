Name:       xcursorgen
Version:    1.0.9
Release:    1
Summary:    Generate X11 cursor files from PNGs
License:    MIT
Prefix:     /usr
Source0:    xcursorgen-1.0.9.tar.xz



%description
Generate X11 cursor files from PNGs.

xcursorgen is maintained at its BLFS r13.1 version and is built
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

%files -f %{_sourcedir}/xcursorgen.filelist
%changelog
# let's skip this for now

