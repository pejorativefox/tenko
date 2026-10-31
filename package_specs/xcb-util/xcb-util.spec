Name:       xcb-util
Version:    0.4.1
Release:    1
Summary:    XCB utilities
License:    GPL3
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz

%description
XCB utilities

%prep
%setup -q

%build
%configure 
%make_build

%install    
rm -rf %{buildroot}
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xcb-util.filelist

%changelog
* Wed Sep 6 2023 Chris Statzer <chris.statzer@gmail.com> 0.4.1-1
- Version bump
