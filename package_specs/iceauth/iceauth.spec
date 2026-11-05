Name:       iceauth
Version:    1.0.11
Release:    2
Summary:    X11 ICE authorization file editor
License:    X11
Prefix:     /usr
Source0:    iceauth-1.0.11.tar.xz



%description
The iceauth program is used to edit and display the authorization
information used in connecting with ICE (the X11 Inter-Client Exchange
protocol). It operates much like the xauth program for X11 connection
authentication records.

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
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.0.11-2
- Replace the TODO summary/description and record the verified license
  (X11): COPYING (issue #8).

# let's skip this for now

