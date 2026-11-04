Name:       iceauth
Version:    1.0.11
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    iceauth-1.0.11.tar.xz



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

%files -f %{_sourcedir}/iceauth.filelist

%changelog
# let's skip this for now

