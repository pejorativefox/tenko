Name:       xkill
Version:    1.0.7
Release:    1
Summary:    Ask an X server to terminate a client
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xkill
Prefix:     /usr
Source0:    xkill-1.0.7.tar.xz



%description
Ask an X server to terminate a client.

xkill is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xkill.filelist
%changelog
# let's skip this for now

