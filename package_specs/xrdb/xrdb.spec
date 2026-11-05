Name:       xrdb
Version:    1.2.3
Release:    2
Summary:    X server resource database utility
License:    MIT
Prefix:     /usr
Source0:    %{name}-%{version}.tar.xz



%description
xrdb is used to get or set the contents of the RESOURCE_MANAGER property on
the root window of screen 0, or the SCREEN_RESOURCES property on the root
window of any or all screens. X clients use these properties to obtain user
preferences for colors, fonts and other resources.

%prep
%setup -a 0

%build
%configure 
%make_build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%make_install
rm -vf %{buildroot}%{_infodir}/dir*

%files -f %{_sourcedir}/xrdb.filelist

%changelog
* Thu Nov 05 2026 browneye <build@browneye.invalid> 1.2.3-2
- Replace the TODO summary/description and record the verified license
  (MIT): COPYING (issue #8).

# let's skip this for now

