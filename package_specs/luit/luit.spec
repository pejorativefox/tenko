Name:       luit
Version:    20260907
Release:    1
Summary:    Encoding converter for X11 terminals
License:    MIT
URL:        https://invisible-island.net/luit/
Prefix:     /usr
Source0:    luit-20260907.tgz



%description
Encoding converter for X11 terminals.

luit is maintained at its pinned version and is built
with the standard autotools build inline in its spec.


%prep
%setup -q

%build
sed -i -e "/D_XOPEN/s/5/6/" configure
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/luit.filelist
%changelog
# let's skip this for now

