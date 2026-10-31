Name:       xkbcomp
Version:    1.5.0
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz



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

%files -f %{_sourcedir}/xkbcomp.filelist

%changelog
# let's skip this for now

