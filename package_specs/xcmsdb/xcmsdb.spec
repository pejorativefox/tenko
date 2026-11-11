Name:       xcmsdb
Version:    1.0.7
Release:    1
Summary:    Query and modify the X11 colour raster database
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xcmsdb
Prefix:     /usr
Source0:    xcmsdb-1.0.7.tar.xz



%description
Query and modify the X11 colour raster database.

xcmsdb is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xcmsdb.filelist
%changelog
# let's skip this for now

