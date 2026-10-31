Name:       libxcb
Version:    1.17.0
Release:    1
Summary:    X11 client library
License:    GPL3
Source0:    %{name}-%{version}.tar.xz
Prefix:     /usr

%description
X11 client library

%prep
%setup -q

%build 
%configure --without-doxygen
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxcb.filelist


%changelog
* Sat Oct 31 2026 browneye <build@browneye.invalid> 1.17.0
- Sync with BLFS r13.1 (1.15)

# let's skip this for now
