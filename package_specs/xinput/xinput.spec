Name:       xinput
Version:    1.6.4
Release:    1
Summary:    Configure and test X11 input devices
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xinput
Prefix:     /usr
Source0:    xinput-1.6.4.tar.xz



%description
Configure and test X11 input devices.

xinput is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xinput.filelist
%changelog
# let's skip this for now

