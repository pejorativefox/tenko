Name:       xkbevd
Version:    1.1.6
Release:    1
Summary:    X11 keyboard event daemon
License:    MIT
Prefix:     /usr
Source0:    xkbevd-1.1.6.tar.xz



%description
X11 keyboard event daemon.

xkbevd is maintained at its BLFS r13.1 version and is built
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

%files -f %{_sourcedir}/xkbevd.filelist
%changelog
# let's skip this for now

