Name:       font-adobe-utopia-type1
Version:    1.0.5
Release:    1
Summary:    Adobe Utopia Type1 fonts for X11
License:    GPL3
Prefix:     /usr
Source0:    font-adobe-utopia-type1-1.0.5.tar.xz



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

%files -f %{_sourcedir}/font-adobe-utopia-type1.filelist
%changelog
# let's skip this for now

