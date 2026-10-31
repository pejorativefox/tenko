Name:       startup-notification
Version:    0.12
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.gz

%description
TODO

%prep
%setup -q

%build
%configure
%make_build


%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files
/usr/

%changelog
# let's skip this for now

