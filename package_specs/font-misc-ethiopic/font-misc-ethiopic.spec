Name:       font-misc-ethiopic
Version:    1.0.5
Release:    1
Summary:    Unicode Ethiopic fonts (Abyssinica SIL-based)
License:    GPL3
Prefix:     /usr
Source0:    font-misc-ethiopic-1.0.5.tar.xz



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

%files -f %{_sourcedir}/font-misc-ethiopic.filelist
%changelog
# let's skip this for now

