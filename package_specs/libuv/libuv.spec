Name:       libuv
Version:    1.52.1
Release:    1
Summary:    TODO
License:    GPL3
Prefix:     /usr
Source0:    %{name}-v%{version}.tar.gz



%description
TODO

%prep
%setup -q -n libuv-v%{version}


%build
sh autogen.sh
%configure --disable-static
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libuv.filelist


%changelog
# let's skip this for now
