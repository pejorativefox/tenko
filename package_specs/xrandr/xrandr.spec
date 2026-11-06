Name:       xrandr
Version:    1.5.4
Release:    1
Summary:    Command line interface to the X11 RandR extension
License:    MIT
Prefix:     /usr
Source0:    xrandr-1.5.4.tar.xz



%description
Command line interface to the X11 RandR extension.

xrandr is maintained at its pinned version and is built
with the standard autotools build inline in its spec.


%prep
%setup -n xrandr-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xrandr.filelist
%changelog
# let's skip this for now

