Name:       font-ibm-type1
Version:    1.0.4
Release:    1
Summary:    IBM Type1 fonts for X11
License:    GPL3
Prefix:     /usr
Source0:    font-ibm-type1-1.0.4.tar.xz



%description
TODO

%prep
%setup -a 0

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*
rm -rf %{buildroot}/usr/share/fonts/X11/Type1/fonts.dir
rm -rf %{buildroot}/usr/share/fonts/X11/Type1/fonts.scale

%files -f %{_sourcedir}/font-ibm-type1.filelist
%changelog
# let's skip this for now

