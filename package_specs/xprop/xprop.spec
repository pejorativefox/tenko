Name:       xprop
Version:    1.2.8
Release:    1
Summary:    Display window and font properties of an X server
License:    MIT
Prefix:     /usr
Source0:    xprop-1.2.8.tar.xz



%description
Display window and font properties of an X server.

xprop is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xprop.filelist
%changelog
# let's skip this for now

