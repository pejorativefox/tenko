Name:       sessreg
Version:    1.1.4
Release:    1
Summary:    Register user sessions in utmp/wtmp
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/sessreg
Prefix:     /usr
Source0:    sessreg-1.1.4.tar.xz



%description
Register user sessions in utmp/wtmp.

sessreg is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/sessreg.filelist
%changelog
# let's skip this for now

