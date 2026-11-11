Name:       smproxy
Version:    1.0.8
Release:    1
Summary:    X11 session manager proxy
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/smproxy
Prefix:     /usr
Source0:    smproxy-1.0.8.tar.xz



%description
X11 session manager proxy.

smproxy is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/smproxy.filelist
%changelog
# let's skip this for now

