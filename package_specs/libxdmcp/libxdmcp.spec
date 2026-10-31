Name:       libXdmcp
Version:    1.1.5
Release:    1
Summary:    TODO
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
TODO

%prep
%setup -q -a0

%build 
%configure
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxdmcp.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.1.5
- Sync with BLFS r13.1 (1.1.2)

# let's skip this for now
