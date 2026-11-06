Name:       xbitmaps
Version:    1.1.4
Release:    1
Summary:    Core X11 bitmap image data
License:    MIT
Prefix:     /usr
Source0:    xbitmaps-1.1.4.tar.xz



%description
Core X11 bitmap image data.

xbitmaps is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xbitmaps.filelist
%changelog
# let's skip this for now
