Name:       xlsatoms
Version:    1.1.5
Release:    1
Summary:    List interned X atoms
License:    MIT
URL:        https://gitlab.freedesktop.org/xorg/app/xlsatoms
Prefix:     /usr
Source0:    xlsatoms-1.1.5.tar.xz



%description
List interned X atoms.

xlsatoms is maintained at its pinned version and is built
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

%files -f %{_sourcedir}/xlsatoms.filelist
%changelog
# let's skip this for now

