Name:       xkbutils
Version:    1.0.7
Release:    1
Summary:    X11 keyboard utility programs
License:    MIT
Prefix:     /usr
Source0:    xkbutils-1.0.7.tar.xz



%description
X11 keyboard utility programs.

xkbutils is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xkbutils.filelist
%changelog
# let's skip this for now

