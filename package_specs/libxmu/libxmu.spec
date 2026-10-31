Name:       libxmu
Version:    1.3.1
Release:    1
Summary:    Xlib misc utilities
License:    GPL3
Prefix:     /usr
Source0:    libXmu-%{version}.tar.xz

BuildRequires: libxt

%description
This library contains miscellaneous utilities and is not part of the Xlib standard. 

%prep
%setup -q -n libXmu-%{version}

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/libxmu.filelist

%changelog
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 1.1.4-1
- Version bump
